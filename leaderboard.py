import requests
import time
import csv
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Google Sheets published URL
google_sheets_url = os.environ.get("GOOGLE_SHEETS_URL", "default_google_sheets_url")
local_filename = os.environ.get("LOCAL_FILENAME", "default_local_filename")

def requests_retry_session(
    retries=10,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_file(url, local_filename):
    try:
        response = requests_retry_session().get(url, stream=True)
        response.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return local_filename
    except requests.exceptions.RequestException as e:
        print("Error downloading file: {}".format(e))
        return None

def parse_time_to_seconds(time_str):
    """Convert MM:SS format to total seconds."""
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds

def print_csv_contents(local_filename):
    with open(local_filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        if rows:
            # Extract header and data rows
            header = rows[0][1:]  # Exclude the first column (Timestamp)
            data = [row[1:] for row in rows[1:]]  # Exclude Timestamp from data rows

            # Keep only the row with the lowest Time for each Name (case-insensitive)
            name_to_best_row = {}
            for row in data:
                name = row[0].strip().lower()  # Normalize name (case-insensitive)
                time_str = row[1]  # Assuming 'Time' is now the second column
                time_seconds = parse_time_to_seconds(time_str)

                if name not in name_to_best_row or time_seconds < parse_time_to_seconds(name_to_best_row[name][1]):
                    name_to_best_row[name] = row

            # Sort the rows by Time (shortest to longest)
            sorted_rows = sorted(name_to_best_row.values(), key=lambda r: parse_time_to_seconds(r[1]))

            # Calculate column widths for pretty printing
            col_widths = [max(len(str(value)) for value in col) for col in zip(header, *sorted_rows)]

            # Print the header
            print(" | ".join(str(value).ljust(col_width) for value, col_width in zip(header, col_widths)))

            # Print each row
            for row in sorted_rows:
                print(" | ".join(str(value).ljust(col_width) for value, col_width in zip(row, col_widths)))

def clear_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = """
    _____  __          _       
   / ___/ / /_ ____ _ (_) _____ ____ |              0         ___|
   \__ \ / __// __ `// // ___// ___/ |             /|\    ___|
  ___/ // /_ / /_/ // // /   (__  )  |             / \___|
 /____/ \__/ \__,_//_//_/   /____/   |            ___|
                                     |       ___|
                                     |  ___|
    """
    print(banner)

def main():
    while True:
        # Clear the terminal window
        clear_terminal()

        print_banner()

        # Download the file from Google Sheets every 10 minutes
        print("Downloading file from Google Sheets...")
        if download_file(google_sheets_url, local_filename):
            # Print the contents of the CSV
            print("CSV Contents (Last updated: {}):".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            print("\n")
            print_csv_contents(local_filename)
        else:
            print("Failed to download file. Retrying in 10 minutes...")

        # Wait for 10 minutes before updating again
        time.sleep(600)

if __name__ == "__main__":
    main()
