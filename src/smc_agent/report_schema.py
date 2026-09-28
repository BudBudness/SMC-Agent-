"""Stable machine-readable intelligence report schema."""
SCHEMA_VERSION="1.0"
REQUIRED=("symbol","timestamp","market_state","liquidity","events","macro","hypotheses","conclusion")
def validate_report(report):
    missing=[k for k in REQUIRED if k not in report]
    return {"valid":not missing,"missing":missing,"schema_version":SCHEMA_VERSION}
