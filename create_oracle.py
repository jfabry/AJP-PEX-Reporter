"""
Fetches live data from the API and saves it as a JSON test oracle.
Run this once to generate oracle data for use in tests.
"""
import json
from config import API_BASE_URL, API_KEY
from main import APIFetcher, PERIODO

fetcher = APIFetcher(API_BASE_URL, API_KEY)

data = fetcher.fetch_data('cursos_dictados', params={'periodo': PERIODO})
filtered_cc = fetcher.filter_data(data, lambda x:
    str(x.get('codigo', '')).startswith('CC') and
    str(x.get('id_cargo', '')) == '1'
)

with open('oracle.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_cc, f, ensure_ascii=False, indent=2)

print(f"Oracle saved: {len(filtered_cc)} filtered CC records")
