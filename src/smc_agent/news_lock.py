from datetime import timedelta
TIER1={"FOMC","FED_RATE","ECB","ECB_RATE","CPI","CORE_CPI","PCE","CORE_PCE","NFP","GDP","PMI","UNEMPLOYMENT","WAGES"}
def news_lock(events,now,minutes=15):
    for e in events or []:
        if str(e.get("importance","")).upper() not in {"HIGH","TIER1"} and str(e.get("tier","")).upper()!="TIER1": continue
        ts=e.get("time"); name=str(e.get("name","")).upper().strip()
        if ts is not None and (name in TIER1 or e.get("tier")=="TIER1") and abs(ts-now)<=timedelta(minutes=minutes): return True,e
    return False,None
