from datetime import timedelta

TIER1={"FOMC","ECB","CPI","CORE CPI","PCE","CORE PCE","NFP","GDP","PMI"}

def news_lock(events,now,minutes=15):
    for e in events or []:
        name=str(e.get("name","")).upper()
        ts=e.get("time")
        if name in TIER1 and ts is not None and abs(ts-now)<=timedelta(minutes=minutes):
            return True,e
    return False,None
