"""
API Data Reporter - Fetch data from REST API and generate CSV reports
"""
import os
import csv
import requests
from config import API_BASE_URL, API_KEY
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


# ============================================================================
# CONFIGURATION: Update this value for different query periods
# ============================================================================
PERIODO = "2025.1"  # Format: YYYY.S (e.g., "2025.1" for first semester 2025)
# ============================================================================


class APIDataReporter:
    """Main class for fetching API data and generating reports"""

    def __init__(self, api_base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API reporter

        Args:
            api_base_url: Base URL for the API
            api_key: API key for authentication (can also use env var API_KEY)
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key or os.getenv('API_KEY')
        self.session = requests.Session()

        # Set up authentication headers
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })

        self.data = []

    def fetch_data(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Fetch data from API endpoint

        Args:
            endpoint: API endpoint path (e.g., '/users', '/posts')
            params: Optional query parameters

        Returns:
            List of data records
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"

        try:
            print(f"Fetching data from {url}...")
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Handle both list and dict responses
            if isinstance(data, dict):
                # If response has a 'data' or 'results' key, use that
                if 'data' in data:
                    data = data['data']
                elif 'results' in data:
                    data = data['results']
                else:
                    # Otherwise wrap single object in list
                    data = [data]

            self.data = data
            print(f"Successfully fetched {len(self.data)} records")
            return self.data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def filter_data(self, filter_func) -> List[Dict]:
        """
        Filter data using a custom function

        Args:
            filter_func: Function that takes a record and returns True/False

        Returns:
            Filtered list of records
        """
        return [record for record in self.data if filter_func(record)]

    def generate_csv_report(
        self,
        filename: str,
        data: Optional[List[Dict]] = None,
        fields: Optional[List[str]] = None,
        output_dir: str = "reports"
    ) -> str:
        """
        Generate a CSV report from data

        Args:
            filename: Name of the CSV file
            data: Data to write (uses self.data if not provided)
            fields: Specific fields to include (uses all fields if not provided)
            output_dir: Directory to save reports

        Returns:
            Path to the generated CSV file
        """
        if data is None:
            data = self.data

        if not data:
            print("No data to write to CSV")
            return ""

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)

        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{filename}_{timestamp}.csv"
        filepath = os.path.join(output_dir, csv_filename)

        # Determine fields to write
        if fields is None:
            # Get all unique keys from all records
            fields = list(set().union(*(record.keys() for record in data)))

        # Write CSV
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)

            print(f"Report generated: {filepath}")
            return filepath

        except Exception as e:
            print(f"Error generating CSV: {e}")
            return ""


if __name__ == "__main__":
    print("=== Running UCampus Mufasa API Reporter ===\n")

    # STEP 2: Initialize reporter
    reporter = APIDataReporter(API_BASE_URL, API_KEY)

    # STEP 3: Fetch your data
    # Fetch cursos_dictados (taught courses) for the specified period
    params = {
        'periodo': PERIODO
    }
    reporter.fetch_data('cursos_dictados', params=params)

    # STEP 4: Generate your custom reports

    # Filter for courses where codigo starts with "CC" and cargo starts with "Profesor"
    # but exclude "Profesor Auxiliar"
    filtered_cc = reporter.filter_data(lambda x:
        str(x.get('codigo', '')).startswith('CC') and
        str(x.get('cargo', '')) != 'Profesor Auxiliar' and
        str(x.get('cargo', '')).startswith('Profesor')
    )

    # Generate report with filtered CC courses taught by professors
    reporter.generate_csv_report('cc_courses_report', data=filtered_cc)
