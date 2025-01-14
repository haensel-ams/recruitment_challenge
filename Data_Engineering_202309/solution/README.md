# Attribution Pipeline Orchestration Tool

## Overview

This Python-based tool is designed as a test challenge for a Data Engineer position, focusing on building a data pipeline to handle customer journey attribution. The pipeline integrates session and conversion data, interacts with an API for attribution modeling, and generates aggregated channel reporting metrics. The application is modular and structured to support orchestration tools such as Airflow, ensuring scalability and robust data validation for accurate insights.

---

## Features

1. **Data Extraction and Filtering**
   - Retrieves session and conversion data from a SQLite database.
   - Supports optional filtering by a specified date range.

2. **Customer Journey Construction**
   - Matches session data with conversion data to form customer journeys.
   - Identifies the last session before a conversion and marks it as the closest session.

3. **Attribution Modeling**
   - Sends customer journey data to an external API for IHC (Incremental Hidden Contribution) attribution.
   - Validates the API results to ensure the sum of IHC values equals 1 for each conversion.

4. **Channel Reporting**
   - Generates aggregated channel reporting metrics, including cost, revenue, CPO (Cost Per Order), and ROAS (Return on Advertising Spend).
   - Saves results to the database and exports to a CSV file.

5. **Chunked API Requests**
   - Splits large data payloads into smaller chunks for API requests to optimize performance and prevent timeouts.

---

## Requirements

- Python 3.7+
- Dependencies:
  - `pandas`
  - `requests`
  - `sqlite3`
  - `argparse`

Install dependencies using pip:
```bash
pip install pandas requests
```

- Environmental variables:
  - `IHC_API_KEY`: Your API key for accessing the IHC API.
  - `API_CONV_ID`: (Optional) Conversion type ID for the API. Defaults to `coding_challenge`.
  - `DB_PATH`: (Optional) Path to the SQLite database. Defaults to `../challenge.db`.

---

## Usage

Run the script with optional start and end dates to process customer journey data:
```bash
python pipeline.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Arguments:
- `--start-date`: Start date for filtering data (format: `YYYY-MM-DD`).
- `--end-date`: End date for filtering data (format: `YYYY-MM-DD`).

Example:
```bash
python pipeline.py --start-date 2023-09-01 --end-date 2023-09-30
```

---

## Functionality Details

### Data Filtering
- Filters session and conversion data by a specified date range using the `_filter_data_by_date` function.

### Customer Journey Construction
- Merges session and conversion data on `user_id`.
- Identifies the last session before a conversion and marks it as a conversion event.

### Attribution Modeling
- Sends customer journeys to the IHC API in chunks of 100 records.
- Validates API results to ensure data integrity.

### Channel Reporting
- Aggregates metrics like cost, IHC, and revenue for each channel.
- Computes derived metrics such as CPO and ROAS.
- Saves results to a CSV file for further analysis.

---

## Assumptions and Challenges

1. **No Training Set Provided**:
   - The IHC API setup did not include a predefined training set. The `customer_journeys` dataset was used as a substitute for training purposes.

2. **No Specified Conversion Session**:
   - The challenge did not specify the exact session linked to a conversion. The closest session to the conversion timestamp was used for this purpose.

3. **IHC Sum Validation Issue**:
   - In some cases, the sum of the `ihc` column in the `attribution_customer_journey` table exceeded 1.0 (100%). This could be due to the use of an incorrect training set, as the task requirement specifies that the sum should equal 1.0 for each `conv_id`.

---

## Logging

The tool uses Python's `logging` module to log events at different levels:
- `INFO`: Logs progress and key actions.
- `WARNING`: Logs issues such as partial API errors or database integrity warnings.
- `ERROR`: Logs API request failures.

---

## Database Schema

The tool interacts with the following database tables:
- **`conversions`**: Stores conversion data.
- **`session_sources`**: Stores session data.
- **`channel_reporting`**: Stores aggregated channel metrics.
- **`attribution_customer_journey`**: Stores attribution results from the API.

---

## Output

1. **Channel Reporting CSV**
   - Generated channel metrics are exported to a file named `channel_reporting.csv`.

2. **Logs**
   - Detailed logs of the execution process are displayed in the console.

---

## Error Handling

- API request errors are logged with detailed messages.
- Partial API errors are captured and logged for analysis.
- Database integrity errors, such as duplicate records, are handled gracefully.

---

## Potential Improvements

1. **Close the Database Connection**
   - Use a context manager (e.g., `with sqlite3.connect(...)`) in database-related functions to ensure that the connection is properly closed after operations.

2. **Optimize API Calls**
   - Implement exponential backoff for retries in the `send_to_api` function using libraries like `tenacity` to handle failures more robustly.

3. **Modularize the Code**
   - Split the code into separate modules:
     - `database.py` for database interactions.
     - `api.py` for API-related functions.
     - `processing.py` for data transformation.

4. **Improve SQL Performance**
   - Ensure indexing on frequently queried columns like `session_id`, `conv_id`, and `event_date` to enhance performance.

5. **Handle Timezone in Datetime Operations**
   - Normalize timestamps to a consistent time zone using `pd.to_datetime(...).dt.tz_localize(...)` to avoid mismatches.

6. **Add Unit Tests**
   - Write unit tests for critical functions such as `get_customer_journeys` and `_filter_data_by_date` to ensure correctness.

7. **Avoid Records Duplication**
   - Add checks to prevent inserting duplicate records into the database tables.

8. **Monitoring and Alerts**
   - Implement monitoring for pipeline execution and set up alerts for failures or anomalies.
