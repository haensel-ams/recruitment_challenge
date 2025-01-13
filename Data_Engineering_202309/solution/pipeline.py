from datetime import datetime as dt
import os
import sqlite3

import requests

import pandas as pd


# API setup
API_KEY = os.getenv("IHC_API_KEY")
API_CONV_ID = "coding_challenge"

# Database setup
DB_PATH = os.getenv("DB_PATH", "../challenge.db")
conn = sqlite3.connect(DB_PATH)


def execute_query(query):
    """Execute a query and return the results as a Pandas DataFrame."""
    return pd.read_sql_query(query, conn)


def filter_data_by_date(df, date_column, start_date, end_date):
    """Filter a DataFrame by a specific date range."""
    if start_date and end_date:
        date_filter = (df[date_column] >= start_date) & (
            df[date_column] <= end_date)
    elif start_date:
        date_filter = df[date_column] >= start_date
    elif end_date:
        date_filter = df[date_column] <= end_date
    else:
        return df
    return df.loc[date_filter]


def get_customer_journeys(conversions, sessions):
    """Create customer journeys by matching sessions to conversions."""
    # Merge conversions and sessions on user_id
    merged = sessions.merge(
        conversions, on='user_id', suffixes=('_session', '_conversion')
    )

    # Filter sessions that occurred before the conversion
    filtered = merged[merged['event_timestamp'] < merged['conv_timestamp']]

    # Sort sessions by user_id and event_timestamp
    filtered = filtered.sort_values(by=['user_id', 'event_timestamp'])

    # Identify the last session before the conversion
    filtered['is_closest_session'] = filtered.groupby('user_id')['event_timestamp'] \
        .transform('last') == filtered['event_timestamp']

    # Create the customer journey dictionary
    customer_journeys = filtered.apply(lambda row: {
        "conversion_id": row['conv_id'],
        "session_id": row['session_id'],
        "timestamp": row['event_timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
        "channel_label": row['channel_name'],
        "holder_engagement": row['holder_engagement'],
        "closer_engagement": row['closer_engagement'],
        "conversion": int(row['is_closest_session']),
        "impression_interaction": row['impression_interaction']
    }, axis=1).tolist()

    return customer_journeys


def chunk_data(data, chunk_size):
    """Split data into smaller chunks of specified size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def send_to_api(payloads):
    """Send customer journeys to the IHC API and retrieve attribution results."""
    api_url = f"https://api.ihc-attribution.com/v1/compute_ihc?conv_type_id={API_CONV_ID}"
    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
    results = []

    for payload in payloads:
        try:
            response = requests.post(
                api_url, json={"customer_journeys": payload}, headers=headers)
            response.raise_for_status()
            results.extend(response.json()["value"])
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
    return results


def save_attribution_results(results):
    """Save attribution results from the API into the database."""
    df = pd.DataFrame(results, columns=["conversion_id", "session_id", "ihc"])
    df.rename(columns={"conversion_id": "conv_id",
              "session_id": "session_id", "ihc": "ihc"}, inplace=True)
    # Insert records, ignoring duplicates
    try:
        df.to_sql("attribution_customer_journey", conn, if_exists="append",
                  index=False, chunksize=500, method='multi')
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError encountered: {e}. Ignoring duplicates.")


def generate_channel_reporting():
    """Generate aggregated channel reporting metrics, save to the database."""
    insert_query = """
        INSERT INTO channel_reporting (channel_name, date, cost, ihc, ihc_revenue)
        SELECT
            ss.channel_name,
            ss.event_date AS date,
            COALESCE(SUM(sc.cost), 0) AS cost,
            COALESCE(SUM(acj.ihc), 0) AS ihc,
            COALESCE(SUM(acj.ihc * c.revenue), 0) AS ihc_revenue
        FROM session_sources ss
        LEFT JOIN session_costs sc ON ss.session_id = sc.session_id
        LEFT JOIN attribution_customer_journey acj ON ss.session_id = acj.session_id
        LEFT JOIN conversions c ON acj.conv_id = c.conv_id
        GROUP BY ss.channel_name, ss.event_date;
    """

    # Execute the insert query
    cursor = conn.cursor()
    cursor.execute(insert_query)
    conn.commit()

    # Add CPO and ROAS columns
    reporting = execute_query("SELECT * FROM channel_reporting;")
    reporting["CPO"] = reporting["cost"] / reporting["ihc"]
    reporting["ROAS"] = reporting["ihc_revenue"] / reporting["cost"]
    return reporting


def export_to_csv(df, filename):
    """Export a DataFrame to a CSV file."""
    df.to_csv(filename, index=False, quoting=1, encoding="utf-8")


def main(start_date=None, end_date=None):
    # Extract data
    conversions = execute_query("SELECT * FROM conversions;")
    sessions = execute_query("SELECT * FROM session_sources;")
    conversions['conv_timestamp'] = pd.to_datetime(
        conversions['conv_date'] + ' ' + conversions['conv_time'])
    sessions['event_timestamp'] = pd.to_datetime(
        sessions['event_date'] + ' ' + sessions['event_time'])

    # Filter data by date range
    if start_date or end_date:
        conversions = filter_data_by_date(
            conversions, "conv_timestamp", start_date, end_date)

    # Get customer journeys
    customer_journeys = get_customer_journeys(conversions, sessions)
    # print(len(customer_journeys))

    # Send data to API
    chunked_payloads = list(chunk_data(customer_journeys[:100], chunk_size=100))
    results = send_to_api(chunked_payloads)
    # print(len(results))

    # Save results to DB
    save_attribution_results(results)

    # Generate channel reporting
    reporting = generate_channel_reporting()

    # Save reporting as a CSV file
    export_to_csv(reporting, "channel_reporting.csv")


if __name__ == "__main__":
    start_date = dt(2023, 9, 1)
    end_date = dt(2023, 9, 30)
    main(start_date=start_date, end_date=end_date)
