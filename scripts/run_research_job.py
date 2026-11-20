import argparse
import hashlib
import json
from pathlib import Path

from api.research_engine import execute


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    parameters = json.loads(args.parameters)
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a JSON object")

    result = execute(parameters)
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
        "source": result.get("source"),
    }, indent=2))


if __name__ == "__main__":
    main()
