"""
API Data Reporter - Fetch data from REST API and generate CSV reports
"""
import os
import csv
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import API_BASE_URL, API_KEY
from api_fetcher import APIFetcher

class Reporter:
    """Generates reports from data"""

    def generate_csv_report(
        self,
        filename: str,
        data: List[Dict],
        fields: Optional[List[str]] = None,
        output_dir: str = "reports"
    ) -> str:
        """
        Generate a CSV report from data.

        Args:
            filename: Name of the CSV file
            data: Data to write
            fields: Specific fields to include (uses all fields if not provided)
            output_dir: Directory to save reports

        Returns:
            Path to the generated CSV file
        """
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


def fetch_dictados(fetcher: APIFetcher, periodo: str) -> List[Dict]:
    return fetcher.fetch_and_filter(
        'cursos_dictados',
        {'periodo': periodo},
        lambda x: str(x.get('codigo', '')).startswith('CC') and str(x.get('id_cargo', '')) == '1'
    )


if __name__ == "__main__":
    print("=== Running UCampus Mufasa API Reporter ===\n")

    fetcher = APIFetcher(API_BASE_URL, API_KEY)
    reporter = Reporter()

    filtered_cc = fetch_dictados(fetcher, "2025.1")

    reporter.generate_csv_report('cc_courses_report', data=filtered_cc)
