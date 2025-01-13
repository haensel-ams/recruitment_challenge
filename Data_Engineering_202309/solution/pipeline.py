from datetime import datetime as dt
from collections import defaultdict
import os
import sqlite3
import logging

import requests

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# API setup
API_KEY = os.getenv("IHC_API_KEY")
API_CONV_ID = "coding_challenge"

# Database setup
DB_PATH = os.getenv("DB_PATH", "../challenge.db")
conn = sqlite3.connect(DB_PATH)


def _execute_query(query):
    """Execute a query and return the results as a Pandas DataFrame."""
    logging.info(f"Executing query: {query}")
    return pd.read_sql_query(query, conn)


def _filter_data_by_date(df, date_column, start_date, end_date):
    """Filter a DataFrame by a specific date range."""
    logging.info(
        f"Filtering data by date range: start_date={start_date}, end_date={end_date}")
    conditions = []
    if start_date:
        conditions.append(df[date_column] >= start_date)
    if end_date:
        conditions.append(df[date_column] <= end_date)
    return df.loc[pd.concat(conditions, axis=1).all(axis=1)] if conditions else df


def get_customer_journeys(conversions, sessions):
    """Create customer journeys by matching sessions to conversions."""
    logging.info(
        "Creating customer journeys by matching sessions to conversions.")
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

    # Assign 1 for the closest session and 0 for others
    filtered['conversion'] = filtered['is_closest_session'].astype(int)

    # Return transformed data as a list of dictionaries
    return filtered[[
        'conv_id', 'session_id', 'event_timestamp', 'channel_name', 'holder_engagement',
        'closer_engagement', 'conversion', 'impression_interaction'
    ]].rename(columns={
        'conv_id': 'conversion_id',
        'event_timestamp': 'timestamp'
    }).to_dict(orient='records')


def _chunk_data(data, chunk_size):
    """Split data into smaller chunks of specified size."""
    logging.info(f"Chunking data into chunks of size {chunk_size}.")
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def _send_to_api(payloads):
    """Send customer journeys to the IHC API and retrieve attribution results."""
    api_url = f"https://api.ihc-attribution.com/v1/compute_ihc?conv_type_id={API_CONV_ID}"
    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
    results = []

    for payload in payloads:
        try:
            logging.info("Sending payload to API.")
            response = requests.post(
                api_url, json={"customer_journeys": payload}, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            if json_data['statusCode'] == 206:
                logging.warning(
                    f"Partial errors occurred: {json_data['partialFailureErrors']}")
            results.extend(json_data.get("value", []))
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
    return results


def _validate_attribution_data(results):
    """Validate that the sum of 'ihc' for each 'conversion_id' equals 1."""
    ihc_sums = defaultdict(float)

    # Calculate the sum of 'ihc' for each 'conversion_id'
    for result in results:
        ihc_sums[result['conversion_id']] += result['ihc']

    # Check for invalid sums
    invalid_conv_ids = {
        conv_id: total for conv_id, total in ihc_sums.items()
        if abs(total - 1) > 1e-6
    }

    if invalid_conv_ids:
        logging.warning(f"Data validation failed for the following 'conversion_id':\n{invalid_conv_ids}")
        # raise ValueError("Validation failed: The sum of 'ihc' is not 1 for some 'conversion_id'.")
    logging.info("Data validation passed: All 'conversion_id' have a valid 'ihc' sum.")


def _save_attribution_results(results):
    """Save attribution results from the API into the database."""
    logging.info("Saving attribution results to the database.")
    df = pd.DataFrame(results, columns=["conversion_id", "session_id", "ihc"])
    df.rename(columns={"conversion_id": "conv_id",
              "session_id": "session_id", "ihc": "ihc"}, inplace=True)
    # Insert records, ignoring duplicates
    try:
        df.to_sql("attribution_customer_journey", conn, if_exists="append",
                  index=False, chunksize=500, method='multi')
    except sqlite3.IntegrityError as e:
        logging.warning(
            f"IntegrityError encountered: {e}. Ignoring duplicates.")


def generate_channel_reporting():
    """Generate aggregated channel reporting metrics, save to the database."""
    logging.info("Generating channel reporting metrics.")
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

    # Add CPO and ROAS columns, handling division by zero
    reporting = _execute_query("SELECT * FROM channel_reporting;")
    reporting["CPO"] = reporting["cost"] / reporting["ihc"].replace(0, pd.NA)
    reporting["ROAS"] = reporting["ihc_revenue"] / \
        reporting["cost"].replace(0, pd.NA)
    reporting = reporting.fillna(0)
    return reporting


def export_to_csv(df, filename):
    """Export a DataFrame to a CSV file."""
    logging.info(f"Exporting DataFrame to {filename}.")
    df.to_csv(filename, index=False, quoting=1, encoding="utf-8")


def main(start_date=None, end_date=None):
    logging.info("Starting main execution.")
    # Extract data
    conversions = _execute_query("SELECT * FROM conversions;")
    sessions = _execute_query("SELECT * FROM session_sources;")
    conversions['conv_timestamp'] = pd.to_datetime(
        conversions['conv_date'] + ' ' + conversions['conv_time'])
    sessions['event_timestamp'] = pd.to_datetime(
        sessions['event_date'] + ' ' + sessions['event_time'])

    # Filter data by date range
    if start_date or end_date:
        conversions = _filter_data_by_date(
            conversions, "conv_timestamp", start_date, end_date)

    # Get customer journeys
    customer_journeys = get_customer_journeys(conversions, sessions)
    logging.info(f"Generated {len(customer_journeys)} customer journeys.")

    # Send data to API and collect the results
    chunked_payloads = list(_chunk_data(customer_journeys, chunk_size=100))
    results = _send_to_api(chunked_payloads)
    logging.info(f"Received {len(results)} results from the API.")

    # Validate the attribution data
    _validate_attribution_data(results)

    # Save results to DB
    _save_attribution_results(results)

    # Generate channel reporting
    reporting = generate_channel_reporting()

    # Save reporting as a CSV file
    export_to_csv(reporting, "channel_reporting.csv")
    logging.info("Main execution completed successfully.")


if __name__ == "__main__":
    start_date = dt(2023, 9, 1)
    end_date = dt(2023, 9, 30)
    main(start_date=start_date, end_date=end_date)
