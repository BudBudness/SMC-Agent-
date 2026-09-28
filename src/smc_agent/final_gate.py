REQUIRED=["causal_backtest","cost_model","oos","walk_forward","risk_limits","news_lock","paper_mode","audit_log","dashboard","live_disabled"]
def readiness(checks):
    missing=[x for x in REQUIRED if not checks.get(x,False)]
    return {"ready":not missing,"missing":missing,"live_enabled":False if missing else bool(checks.get("live_enabled",False))}
def assert_not_live():
    import os
    if os.getenv("ENABLE_LIVE_TRADING","false").lower()=="true": raise RuntimeError("Final gate blocks live trading pending explicit deployment review")
