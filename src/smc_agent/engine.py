"""Market intelligence orchestration. No execution or trading-state output."""
import pandas as pd
from .structure import structure_state,swings,choch_bos
from .liquidity import map_liquidity,sweep
from .amd import classify_amd
from .fvg import find_fvg
from .order_blocks import find_order_blocks
from .contradictions import compare
from .timeframes import reconstruct
from .inducement import detect as detect_inducement
from .sequencing import sequence
from .intelligence import build_report,Hypothesis
from .macro import event_context
from .macro_reaction import enrich


def _displacement(df):
    if len(df)<25:return "NONE"
    body=(df.close-df.open).abs()
    atr=(df.high-df.low).rolling(20).mean().iloc[-1]
    if pd.isna(atr) or atr==0:return "NONE"
    ratio=float(body.iloc[-1]/atr)
    return "EXTREME" if ratio>=2.5 else "STRONG" if ratio>=1.8 else "MODERATE" if ratio>=1.3 else "WEAK"

def _location(df):
    if df.empty:
        return "UNKNOWN"
    points=swings(df)
    highs=[p[2] for p in points if p[0]=="HIGH"]
    lows=[p[2] for p in points if p[0]=="LOW"]
    if not highs or not lows:
        return "UNKNOWN"
    high=max(highs[-3:])
    low=min(lows[-3:])
    if high<=low:
        return "UNKNOWN"
    close=float(df.close.iloc[-1])
    mid=(high+low)/2
    return "DISCOUNT" if close<mid else "PREMIUM" if close>mid else "EQUILIBRIUM"

def analyze(df,symbol="EURUSD",news_events=None,now=None):
    df=df.sort_index()
    if len(df)<100:
        return build_report(symbol,now,{"status":"INSUFFICIENT_DATA"} ,{},[],{},[
            Hypothesis("insufficient_data",["fewer than 100 source rows"],[],["validated multi-timeframe history"],0.0)])
    frames=reconstruct(df)
    states={k:structure_state(frames[k]) for k in frames if len(frames[k])>=8}
    contradiction=compare(states)
    weekly=states.get("W","NEUTRAL")
    weekly_swings=swings(frames["W"])
    intraday_swings=swings(frames["15M"])
    zones=map_liquidity(weekly_swings,scope="external")
    zones.extend(map_liquidity(intraday_swings[-40:],scope="internal"))
    sweep_event=sweep(frames["15M"],zones)
    inducement=detect_inducement(zones,sweep_event,{"weekly_bias":weekly})
    shift=choch_bos(frames["15M"],weekly)
    disp=_displacement(frames["15M"])
    fvgs=find_fvg(frames["15M"]); obs=find_order_blocks(frames["15M"])
    amd=classify_amd(frames["4H"])
    events=[]
    if weekly_swings:
        events.append({"name":"liquidity_formation","time":weekly_swings[-1][1],"timeframe":"W","kind":"observation","evidence":{"external_count":len([z for z in zones if z["scope"]=="external"])}})
    if intraday_swings:
        events.append({"name":"internal_liquidity_formation","time":intraday_swings[-1][1],"timeframe":"15M","kind":"observation","evidence":{"internal_count":len([z for z in zones if z["scope"]=="internal"])}})
    if inducement.get("detected"): events.append({"name":"inducement","time":df.index[-1],"timeframe":"15M","kind":"interpretation","evidence":inducement})
    if sweep_event: events.append({"name":"sweep","time":sweep_event["time"],"timeframe":"15M","kind":"observation","evidence":sweep_event})
    if disp!="NONE": events.append({"name":"displacement","time":df.index[-1],"timeframe":"15M","kind":"observation","evidence":{"strength":disp}})
    if shift.get("choch"): events.append({"name":"choch","time":df.index[-1],"timeframe":"15M","kind":"observation","evidence":shift})
    if shift.get("bos"): events.append({"name":"bos","time":df.index[-1],"timeframe":"15M","kind":"observation","evidence":shift})
    if fvgs: events.append({"name":"fvg","time":fvgs[-1].get("time",df.index[-1]) if isinstance(fvgs[-1],dict) else df.index[-1],"timeframe":"15M","kind":"observation","evidence":fvgs[-1]})
    events=sequence(events)["events"]
    macro=enrich(event_context(news_events))
    evidence=[]
    if weekly!="NEUTRAL": evidence.append(f"Weekly structure={weekly}")
    if sweep_event: evidence.append(f"15M liquidity sweep={sweep_event['kind']}")
    if shift.get("choch") or shift.get("bos"): evidence.append(f"15M structure event CHoCH={shift.get('choch')} BOS={shift.get('bos')}")
    contradictions=contradiction["contradictions"]
    hypotheses=[
        Hypothesis("continuation",evidence,contradictions,["Weekly structure changes","key liquidity is invalidated"]),
        Hypothesis("structural_conflict",[],[] if contradictions else ["no cross-timeframe conflict detected"],["conflicting timeframe resolves"]),
    ]
    state={"weekly_bias":weekly,"timeframes":states,"4H_AMD":amd,"daily_location":_location(frames["D"]),
           "contradictions":contradictions,"authority":"W"}
    liquidity={"zones":zones,"sweep":sweep_event,"inducement":inducement}
    report=build_report(symbol,now or df.index[-1],state,liquidity,events,macro,hypotheses)
    report.market_state["displacement"]=disp
    report.market_state["fvg_count"]=len(fvgs)
    report.market_state["order_block_count"]=len(obs)
    return report
