import pytest
from core.forecast import forecast, validate_observations

BASE = {"platform_id":"P1", "capacity_threshold":100, "horizon_minutes":10, "observations":[
 {"timestamp":"2026-10-14T10:00:00+00:00","platform_id":"P1","passenger_count":20},
 {"timestamp":"2026-10-14T10:05:00+00:00","platform_id":"P1","passenger_count":40},
 {"timestamp":"2026-10-14T10:10:00+00:00","platform_id":"P1","passenger_count":60}]}

def test_forecast_basic():
    out = forecast(BASE)
    assert out["estimated_passengers"] > 0
    assert out["congestion_band"] in {"low","moderate","high","at_or_above_threshold"}

def test_threshold_band():
    x = {**BASE, "capacity_threshold": 10}
    assert forecast(x)["congestion_band"] == "at_or_above_threshold"

def test_wrong_platform_ignored():
    x = {**BASE, "observations":[{**BASE["observations"][0], "platform_id":"P2"}]}
    with pytest.raises(ValueError): forecast(x)

def test_negative_count_rejected():
    x = {**BASE, "observations":[{**BASE["observations"][0], "passenger_count":-1}]}
    with pytest.raises(ValueError): forecast(x)

def test_bad_threshold_rejected():
    with pytest.raises(ValueError): forecast({**BASE, "capacity_threshold":0})

def test_bad_uplift_rejected():
    with pytest.raises(ValueError): forecast({**BASE, "uplift_factor":-1})

def test_duplicate_timestamp_reported():
    rows = BASE["observations"] + [BASE["observations"][0]]
    result = validate_observations(rows, "P1")
    assert len(result["valid"]) == 3
    assert any("duplicate" in f for f in result["findings"])

def test_evidence_and_limitations_present():
    out = forecast(BASE)
    assert out["evidence"]["valid_observation_count"] == 3
    assert out["limitations"]
