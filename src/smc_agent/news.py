TIER1={"FOMC","FED_RATE","ECB_RATE","CPI","CORE_CPI","PCE","CORE_PCE","NFP","GDP"}
def news_lock(events,now,before=15,after=15):
    for e in events:
        if e.get("importance")=="HIGH":
            minutes=abs((now-e["time"]).total_seconds())/60
            if minutes<=max(before,after): return True,e
    return False,None
