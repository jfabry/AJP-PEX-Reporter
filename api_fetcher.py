import requests
from typing import List, Dict, Optional


class APIFetcher:
    """Fetches and filters data from a REST API"""

    def __init__(self, api_base_url: str, api_key: str):
        """
        Args:
            api_base_url: Base URL for the API
            api_key: API key for authentication
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def fetch_data(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Fetch data from an API endpoint.

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

            print(f"Successfully fetched {len(data)} records")
            return data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_and_filter(self, endpoint: str, params: Optional[Dict], filter_func) -> List[Dict]:
        """
        Fetch data from an API endpoint and filter it.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            filter_func: Function that takes a record and returns True/False

        Returns:
            Filtered list of records
        """
        data = self.fetch_data(endpoint, params=params)
        return self.filter_data(data, filter_func)

    def filter_data(self, data: List[Dict], filter_func) -> List[Dict]:
        """
        Filter data using a custom function.

        Args:
            data: List of records to filter
            filter_func: Function that takes a record and returns True/False

        Returns:
            Filtered list of records
        """
        return [record for record in data if filter_func(record)]
