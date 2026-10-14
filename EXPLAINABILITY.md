# Explainability

## Inputs
The agent uses timestamped platform passenger counts, platform identifiers, optional scheduled-arrival/event indicators, and an operator-supplied capacity threshold. Counts and thresholds must use consistent units.

## Decision
The baseline forecast is a recency-weighted average of recent observations for the requested platform, with optional supplied uplift factors applied only when present. Congestion bands are assigned by comparing the estimated count to the configured threshold. This is a transparent heuristic, not a trained or calibrated forecasting model.

## Limits
Sparse samples, irregular intervals, special events, cancellations, sensor failures, and sudden passenger surges can invalidate the estimate. Capacity thresholds must be set by authorized railway personnel. Outputs do not replace real-time monitoring or railway safety procedures.

## Tool: validate-observations
### Inputs and Data Sources
A list of timestamped platform count records.
### Decision and Reasoning
Checks required fields, non-negative counts, parseable timestamps, and consistent platform identifiers.
### Outputs and Evidence
Validation findings and usable observation count.
### Limits and Constraints
Does not verify sensor accuracy or actual timestamps.
### Failure Handling
Reports invalid rows instead of silently treating them as valid.
### Human Review
Investigate missing, duplicate, or implausible observations.

## Tool: forecast-platform-congestion
### Inputs and Data Sources
Recent counts, target platform, capacity threshold, and forecast horizon.
### Decision and Reasoning
Computes a recency-weighted baseline and threshold-based congestion band.
### Outputs and Evidence
Estimated count, band, contributing observations, and confidence label.
### Limits and Constraints
No external live timetable or sensor integration; no statistical calibration.
### Failure Handling
Returns an explicit error for absent usable observations or invalid threshold.
### Human Review
Compare with station displays, CCTV-derived aggregate counts where authorized, and live operations information.

## Tool: generate-operations-brief
### Inputs and Data Sources
Forecast output and optional operator notes.
### Decision and Reasoning
Maps elevated estimated crowding to advisory review suggestions.
### Outputs and Evidence
A concise brief with triggers, caveats, and recommended checks.
### Limits and Constraints
Cannot determine safe capacity or issue control instructions.
### Failure Handling
Marks missing fields and uncertainty in the brief.
### Human Review
Authorized station operations staff decide and execute any action.
