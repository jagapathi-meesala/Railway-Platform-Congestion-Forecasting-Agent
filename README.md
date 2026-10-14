# Railway Platform Congestion Forecasting Agent

A small, explainable Python agent that estimates short-horizon platform crowding from supplied historical aggregate passenger counts and produces an advisory operations brief.

## Features
- Input validation for platform observations.
- Recency-weighted baseline estimate.
- Operator-configured crowding thresholds.
- Confidence label based on sample quantity and recency.
- JSON output with evidence and advisory notes.

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m core.cli examples/platform_case.json --output report.json
```

## Input format
JSON object containing `platform_id`, `capacity_threshold`, `horizon_minutes`, and `observations` (`timestamp`, `platform_id`, `passenger_count`). Optional `uplift_factor` can represent an operator-supplied event/timetable adjustment; it is not inferred automatically.

## Safety and limitations
This is a heuristic demonstration, not a validated safety-critical forecasting system. It does not connect to railway systems, issue commands, or replace real-time monitoring. Thresholds and operational responses must be approved by railway personnel. Test on historical data and evaluate error before operational use.
