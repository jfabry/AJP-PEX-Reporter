import json
import pytest
from unittest.mock import MagicMock
from config import API_BASE_URL, API_KEY
from api_fetcher import APIFetcher
from main import fetch_dictados


# ---------------------------------------------------------------------------
# APIFetcher
# ---------------------------------------------------------------------------

class TestAPIFetcherInit:
    def test_sets_base_url(self):
        fetcher = APIFetcher("https://example.com/api/", "key")
        assert fetcher.api_base_url == "https://example.com/api"

    def test_strips_trailing_slash(self):
        fetcher = APIFetcher("https://example.com/api/", "key")
        assert not fetcher.api_base_url.endswith('/')

    def test_sets_auth_header(self):
        fetcher = APIFetcher("https://example.com", "mykey")
        assert fetcher.session.headers['Authorization'] == 'Bearer mykey'


class TestAPIFetcherFetchData:
    def _make_fetcher(self):
        return APIFetcher("https://example.com", "key")

    def test_returns_list_response(self):
        fetcher = self._make_fetcher()
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1}, {"id": 2}]
        fetcher.session.get = MagicMock(return_value=mock_response)

        result = fetcher.fetch_data("items")
        assert result == [{"id": 1}, {"id": 2}]

    def test_unwraps_data_key(self):
        fetcher = self._make_fetcher()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": 1}]}
        fetcher.session.get = MagicMock(return_value=mock_response)

        result = fetcher.fetch_data("items")
        assert result == [{"id": 1}]

    def test_unwraps_results_key(self):
        fetcher = self._make_fetcher()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": 1}]}
        fetcher.session.get = MagicMock(return_value=mock_response)

        result = fetcher.fetch_data("items")
        assert result == [{"id": 1}]

    def test_wraps_plain_dict_in_list(self):
        fetcher = self._make_fetcher()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "test"}
        fetcher.session.get = MagicMock(return_value=mock_response)

        result = fetcher.fetch_data("items")
        assert result == [{"id": 1, "name": "test"}]

    def test_passes_params_to_request(self):
        fetcher = self._make_fetcher()
        mock_response = MagicMock()
        mock_response.json.return_value = []
        fetcher.session.get = MagicMock(return_value=mock_response)

        fetcher.fetch_data("items", params={"periodo": "2025.1"})
        fetcher.session.get.assert_called_once_with(
            "https://example.com/items", params={"periodo": "2025.1"}
        )

    def test_returns_empty_list_on_error(self):
        import requests
        fetcher = self._make_fetcher()
        fetcher.session.get = MagicMock(side_effect=requests.exceptions.ConnectionError)

        result = fetcher.fetch_data("items")
        assert result == []


# ---------------------------------------------------------------------------
# Sanity check
# ---------------------------------------------------------------------------

def test_fetch_dictados():
    with open('oracle.json', encoding='utf-8') as f:
        oracle = json.load(f)

    fetcher = APIFetcher(API_BASE_URL, API_KEY)
    result = fetch_dictados(fetcher, "2025.1")

    assert result == oracle


def test_sanity_check():
    with open('oracle.json', encoding='utf-8') as f:
        oracle = json.load(f)

    fetcher = APIFetcher(API_BASE_URL, API_KEY)
    result = fetcher.fetch_and_filter(
        'cursos_dictados',
        {'periodo': "2025.1"},
        lambda x: str(x.get('codigo', '')).startswith('CC') and str(x.get('id_cargo', '')) == '1',
    )

    assert result == oracle
