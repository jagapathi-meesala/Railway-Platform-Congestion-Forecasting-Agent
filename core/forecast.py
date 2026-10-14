from datetime import datetime, timezone
from math import isfinite


def parse_timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be valid ISO-8601") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def validate_observations(observations, platform_id):
    findings = []
    valid = []
    if not isinstance(observations, list):
        return {"valid": [], "findings": ["observations must be a list"]}
    seen = set()
    for idx, row in enumerate(observations):
        if not isinstance(row, dict):
            findings.append(f"row {idx}: expected an object")
            continue
        try:
            ts = parse_timestamp(row.get("timestamp"))
            count = row.get("passenger_count")
            if isinstance(count, bool) or not isinstance(count, (int, float)) or not isfinite(count) or count < 0:
                raise ValueError("passenger_count must be a finite non-negative number")
            pid = row.get("platform_id")
            if not isinstance(pid, str) or not pid.strip():
                raise ValueError("platform_id is required")
            if pid != platform_id:
                findings.append(f"row {idx}: platform_id does not match requested platform; ignored")
                continue
            key = (ts.isoformat(), pid)
            if key in seen:
                findings.append(f"row {idx}: duplicate timestamp/platform observation; ignored")
                continue
            seen.add(key)
            valid.append({"timestamp": ts, "passenger_count": float(count), "platform_id": pid, "source_row": idx})
        except (ValueError, TypeError) as exc:
            findings.append(f"row {idx}: {exc}")
    valid.sort(key=lambda x: x["timestamp"])
    return {"valid": valid, "findings": findings}


def forecast(payload):
    platform_id = payload.get("platform_id")
    if not isinstance(platform_id, str) or not platform_id.strip():
        raise ValueError("platform_id is required")
    threshold = payload.get("capacity_threshold")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not isfinite(threshold) or threshold <= 0:
        raise ValueError("capacity_threshold must be a positive finite number")
    horizon = payload.get("horizon_minutes", 15)
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
        raise ValueError("horizon_minutes must be a positive integer")
    checked = validate_observations(payload.get("observations", []), platform_id)
    obs = checked["valid"]
    if not obs:
        raise ValueError("no valid observations for requested platform")
    # More recent samples receive linearly larger weights; oldest gets weight 1.
    weights = list(range(1, len(obs) + 1))
    baseline = sum(o["passenger_count"] * w for o, w in zip(obs, weights)) / sum(weights)
    uplift = payload.get("uplift_factor", 1.0)
    if isinstance(uplift, bool) or not isinstance(uplift, (int, float)) or not isfinite(uplift) or uplift < 0:
        raise ValueError("uplift_factor must be a finite non-negative number")
    estimate = baseline * float(uplift)
    ratio = estimate / float(threshold)
    band = "low" if ratio < 0.5 else "moderate" if ratio < 0.75 else "high" if ratio < 1.0 else "at_or_above_threshold"
    age_hours = max(0.0, (datetime.now(timezone.utc) - obs[-1]["timestamp"].astimezone(timezone.utc)).total_seconds() / 3600)
    confidence = "low" if len(obs) < 3 or age_hours > 6 else "moderate" if len(obs) < 8 or age_hours > 1 else "higher (still uncalibrated)"
    suggestions = []
    if band in ("high", "at_or_above_threshold"):
        suggestions += ["Verify the estimate against current aggregate counts and station monitoring.", "Have authorized station operations staff review passenger-flow arrangements and applicable procedures."]
    elif band == "moderate":
        suggestions += ["Increase monitoring frequency and check upcoming arrivals or known events."]
    else:
        suggestions += ["Continue routine monitoring; reassess if live counts rise or service conditions change."]
    if confidence == "low":
        suggestions.append("Treat this estimate cautiously because observations are sparse or stale.")
    if checked["findings"]:
        suggestions.append("Review input validation findings before relying on this estimate.")
    return {
        "agent": "railway-platform-congestion-forecasting-agent",
        "platform_id": platform_id,
        "horizon_minutes": horizon,
        "estimated_passengers": round(estimate, 2),
        "capacity_threshold": float(threshold),
        "threshold_ratio": round(ratio, 3),
        "congestion_band": band,
        "confidence": confidence,
        "method": "recency-weighted mean of supplied observations multiplied by optional operator-supplied uplift_factor",
        "evidence": {"valid_observation_count": len(obs), "observation_timestamps": [o["timestamp"].isoformat() for o in obs], "validation_findings": checked["findings"], "uplift_factor": float(uplift)},
        "advisory_suggestions": suggestions,
        "limitations": ["Heuristic baseline, not a trained or calibrated forecast", "No live timetable, sensor, CCTV, or railway-system connection", "Threshold is operator-supplied and must be validated locally", "Not for autonomous safety-critical decisions"]
    }
