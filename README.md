# AJP-PEX-Reporter

A Python tool for fetching data from the UCampus Mufasa API and generating CSV reports with filtering capabilities.

## Features

- UCampus Mufasa API integration with authentication
- Data filtering
- Automatic timestamped CSV files in the `reports/` directory

## Installation

```bash
pip3 install -r requirements.txt
```

## Configuration

At the top of [main.py](main.py), update the `PERIODO` variable to the desired query period:

```python
PERIODO = "2025.1"  # Format: YYYY.S (e.g., "2025.1" for first semester 2025)
```

## Running

```bash
python3 main.py
```

This fetches `cursos_dictados` for the configured period and generates `cc_courses_report` in the `reports/` directory, filtered to courses where:
- `codigo` starts with `CC`
- `cargo` starts with `Profesor` (excluding `Profesor Auxiliar`)

## Output

CSV files are saved in the `reports/` directory with timestamps:
- `cc_courses_report_20260210_164329.csv`

## Customization

To change the endpoint or filters, edit the `__main__` block in [main.py](main.py).

### Changing the endpoint

```python
reporter.fetch_data('your-endpoint', params=params)
```

### Changing the filter

```python
filtered = reporter.filter_data(lambda x: x.get('your-field') == 'your-value')
reporter.generate_csv_report('your_report', data=filtered)
```
