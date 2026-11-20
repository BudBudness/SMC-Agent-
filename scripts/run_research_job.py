import argparse
import hashlib
import json
from pathlib import Path

from api.research_engine import execute


def normalize(engine: dict) -> dict:
    report = engine.get("report") or {}
    market = report.get("market_state") or {}
    return {
        "run_version": "2.0",
        "engine_version": engine.get("engine_version"),
        "execution": engine.get("execution"),
        "instrument": (engine.get("parameters") or {}).get("instrument") or report.get("symbol"),
        "dataset": engine.get("source") or {},
        "look_ahead_policy": (engine.get("lineage") or {}).get(
            "lookahead_policy",
            "confirmed swing events expose right-side confirmation timestamps",
        ),
        "mtf": market.get("timeframes") or {},
        "market_state": market,
        "events": report.get("events") or [],
        "evidence": report.get("evidence") or [],
        "benchmarks": engine.get("benchmarks"),
        "replay": engine.get("replay") or [],
        "analogue_research": report.get("analogue_research") or {},
        "hypotheses": report.get("hypotheses") or [],
        "conclusion": report.get("conclusion"),
        "dataset_validation": engine.get("dataset_validation"),
        "mtf_validation": engine.get("mtf_validation"),
        "lineage": [
            {
                "stage": "source",
                "artifact": (engine.get("source") or {}).get("artifact", "validated release dataset"),
                "rows": (engine.get("source") or {}).get("rows_after_window"),
            },
            {"stage": "dataset_validation", "status": "PASS" if (engine.get("dataset_validation") or {}).get("valid") else "FAIL"},
            {"stage": "mtf_reconstruction", "status": "PASS" if (engine.get("mtf_validation") or {}).get("valid") else "FAIL"},
            {"stage": "canonical_engine", "status": "EXECUTED", "version": engine.get("engine_version")},
        ],
        "parameters": engine.get("parameters"),
        "report": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    parameters = json.loads(args.parameters)
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a JSON object")

    result = normalize(execute(parameters))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    output.write_bytes(encoded)
    print(json.dumps({
        "output": str(output),
        "bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "engine_version": result.get("engine_version"),
        "execution": result.get("execution"),
        "source": result.get("dataset"),
    }, indent=2))


if __name__ == "__main__":
    main()
