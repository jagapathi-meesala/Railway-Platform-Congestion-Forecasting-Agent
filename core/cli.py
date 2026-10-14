import argparse, json
from pathlib import Path
from .forecast import forecast


def main():
    parser = argparse.ArgumentParser(description="Forecast railway platform congestion from supplied aggregate observations")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = forecast(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

if __name__ == "__main__":
    main()
