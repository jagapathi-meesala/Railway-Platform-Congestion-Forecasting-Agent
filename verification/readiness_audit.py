from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
required = ["agent.yaml","SOUL.md","RULES.md","DUTIES.md","AGENTS.md","EXPLAINABILITY.md","README.md","requirements.txt","core/__init__.py","core/forecast.py","core/cli.py","tools/validate-observations.yaml","tools/forecast-platform-congestion.yaml","tools/generate-operations-brief.yaml","skills/congestion-forecasting/SKILL.md","skills/risk-assessment/SKILL.md","skills/operations-guidance/SKILL.md","tests/test_forecast.py","examples/platform_case.json"]
missing = [p for p in required if not (ROOT/p).is_file()]
if missing:
    print("FAIL: missing files:", ", ".join(missing)); sys.exit(1)
print(f"PASS: all {len(required)}/{len(required)} required files present")
