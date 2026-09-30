"""Market intelligence orchestration. Research-only; no execution semantics."""
import pandas as pd
from .structure import structure_state,swings,choch_bos
from .liquidity import map_liquidity,sweep
from .amd import classify_amd
from .fvg import find_fvg
from .order_blocks import find_order_blocks
from .displacement import detect_displacement
from .contradictions import compare
from .timeframes import reconstruct
from .inducement import detect as detect_inducement
from .sequencing import sequence
from .intelligence import build_report,Hypothesis
from .macro import event_context
from .macro_reaction import enrich
from .event_study import event_reactions,summarize

def _location(df):
    points=swings(df)
    highs=[p[2] for p in points if p[0]=="HIGH"]; lows=[p[2] for p in points if p[0]=="LOW"]
    if not highs or not lows:return "UNKNOWN"
    hi=max(highs[-3:]); lo=min(lows[-3:])
    if hi<=lo:return "UNKNOWN"
    close=float(df.close.iloc[-1]); mid=(hi+lo)/2
    return "DISCOUNT" if close<mid else "PREMIUM" if close>mid else "EQUILIBRIUM"

def analyze(df,symbol="EURUSD",news_events=None,now=None):
    df=df.sort_index()
    if len(df)<100:
        return build_report(symbol,now,{"status":"INSUFFICIENT_DATA"},{"zones":[],"sweep":None,"inducement":None},[],{},[
            Hypothesis("insufficient_data",["fewer than 100 source rows"],["full research state unavailable"],["provide a validated multi-timeframe history"])])
    frames=reconstruct(df)
    states={k:structure_state(frames[k]) for k in frames if len(frames[k])>=8}
    contradiction=compare(states)
    weekly=states.get("W","NEUTRAL")
    ws=swings(frames["W"]); ins=swings(frames["15M"])
    zones=map_liquidity(ws,scope="external")+map_liquidity(ins[-40:],scope="internal")
    sweep_event=sweep(frames["15M"],zones)
    inducement=detect_inducement(zones,sweep_event,{"weekly_bias":weekly})
    shift=choch_bos(frames["15M"],weekly)
    displacements=detect_displacement(frames["15M"])
    latest_disp=displacements[-1] if displacements else None
    fvgs=find_fvg(frames["15M"])
    obs=find_order_blocks(frames["15M"],displacements)
    amd=classify_amd(frames["4H"])
    events=[]
    if ws: events.append({"name":"liquidity_formation","time":ws[-1][1],"timeframe":"W","kind":"observation","evidence":{"external_count":len(ws)}})
    if ins: events.append({"name":"internal_liquidity_formation","time":ins[-1][1],"timeframe":"15M","kind":"observation","evidence":{"internal_count":len(ins[-40:])}})
    if sweep_event: events.append({"name":"sweep","time":sweep_event["time"],"timeframe":"15M","kind":"observation","evidence":sweep_event})
    if latest_disp: events.append({"name":"displacement","time":latest_disp["time"],"timeframe":"15M","kind":"observation","evidence":latest_disp})
    if shift.get("choch"): events.append({"name":"choch","time":df.index[-1],"timeframe":"15M","kind":"observation","evidence":shift})
    if shift.get("bos"): events.append({"name":"bos","time":df.index[-1],"timeframe":"15M","kind":"observation","evidence":shift})
    if fvgs: events.append({"name":"fvg","time":fvgs[-1]["formed_at"],"timeframe":"15M","kind":"observation","evidence":fvgs[-1]})
    if obs: events.append({"name":"order_block","time":obs[-1]["formed_at"],"timeframe":"15M","kind":"observation","evidence":obs[-1]})
    events=sequence(events)["events"]
    macro={"events":enrich(event_context(news_events))}
    evidence=[]
    if weekly!="NEUTRAL": evidence.append({"claim":"weekly_structure","observation":weekly,"source":"confirmed swing sequence","timeframe":"W"})
    if sweep_event: evidence.append({"claim":"liquidity_sweep","observation":sweep_event["kind"],"source":"chronological liquidity raid","timeframe":"15M"})
    if latest_disp: evidence.append({"claim":"displacement","observation":latest_disp["strength"],"source":"local range/body expansion","timeframe":"15M"})
    if shift.get("choch") or shift.get("bos"): evidence.append({"claim":"structure_break","observation":f"CHoCH={shift.get('choch')} BOS={shift.get('bos')}","source":"close-confirmed swing break","timeframe":"15M"})
    contradictions=contradiction["contradictions"]
    hypotheses=[
        Hypothesis("continuation",evidence,contradictions,["Weekly structure changes","key liquidity is invalidated"]),
        Hypothesis("structural_conflict",[],[] if contradictions else ["no cross-timeframe conflict detected"],["conflicting timeframe resolves"])
    ]
    state={"weekly_bias":weekly,"timeframes":states,"4H_AMD":amd,"daily_location":_location(frames["D"]),
           "contradictions":contradictions,"authority":"W",
           "displacement":latest_disp["strength"] if latest_disp else "NONE",
           "fvg_count":len(fvgs),"order_block_count":len(obs)}
    event_reaction_summary={}
    try:
        reaction=event_reactions(frames["15M"],events)
        event_reaction_summary=summarize(reaction)
    except Exception:
        event_reaction_summary={"samples":0}
    macro["event_reaction_study"]=event_reaction_summary
    liquidity={"zones":zones,"sweep":sweep_event,"inducement":inducement,
               "external_zone_count":len(ws),"internal_zone_count":len(ins[-40:])}
    return build_report(symbol,now or df.index[-1],state,liquidity,events,macro,hypotheses)
