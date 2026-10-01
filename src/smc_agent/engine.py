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
from .intelligence import build_report
from .macro import event_context
from .macro_reaction import enrich
from .event_study import event_reactions,summarize
from .evidence import Evidence,EvidenceLedger
from .analogue import research as analogue_research
from .data_integrity import validate_source

def _location(df):
    points=swings(df)
    highs=[p[2] for p in points if p[0]=="HIGH"]; lows=[p[2] for p in points if p[0]=="LOW"]
    if not highs or not lows:return "UNKNOWN"
    hi=max(highs[-3:]); lo=min(lows[-3:])
    if hi<=lo:return "UNKNOWN"
    close=float(df.close.iloc[-1]); mid=(hi+lo)/2
    return "DISCOUNT" if close<mid else "PREMIUM" if close>mid else "EQUILIBRIUM"

def _evidence(weekly,sweep_event,latest_disp,shift,contradictions,df):
    ledger=EvidenceLedger()
    if weekly!="NEUTRAL":
        ledger.add(Evidence("weekly_structure",weekly,"confirmed swing sequence","W",df.index[-1],
                            "confirmed two-swing HH/HL or LH/LL sequence",strength="HIGH"))
    if sweep_event:
        ledger.add(Evidence("liquidity_sweep",sweep_event.get("kind","observed"),"chronological liquidity raid","15M",
                            sweep_event.get("time"),"liquidity approach/take/rejection",strength="MODERATE"))
    if latest_disp:
        ledger.add(Evidence("displacement",latest_disp["strength"],"local range/body expansion","15M",
                            latest_disp["time"],"rolling pre-event median normalization",strength="MODERATE"))
    if shift.get("choch") or shift.get("bos"):
        ledger.add(Evidence("structure_break",f"CHoCH={shift.get('choch')} BOS={shift.get('bos')}",
                            "close-confirmed swing break","15M",df.index[-1],
                            "confirmed swing reference and close beyond level",strength="MODERATE"))
    if contradictions:
        ledger.add(Evidence("cross_timeframe_conflict",str(len(contradictions)),"cross-timeframe state comparison",
                            "MTF",df.index[-1],"hierarchical timeframe comparison",contradicts=["continuation"],strength="HIGH"))
    return ledger

def analyze(df,symbol="EURUSD",news_events=None,now=None,historical_episodes=None):
    df=df.sort_index()
    source_integrity=validate_source(df)
    if len(df)<100:
        return build_report(symbol,now,{"status":"INSUFFICIENT_DATA"},{"zones":[],"sweep":None,"inducement":None},[],{},
            [{"name":"insufficient_data","evidence":[],"contradictions":[],"invalidation":["provide a validated multi-timeframe history"]}],
            [],{"status":"INSUFFICIENT_SAMPLE","matches":[],"samples":0})
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
    ledger=_evidence(weekly,sweep_event,latest_disp,shift,contradiction["contradictions"],df)
    evidence=ledger.as_list()
    study_events=[e for e in events if e.get("timeframe")=="15M"]
    macro["event_reaction_study"]=summarize(event_reactions(frames["15M"],study_events))
    state={"weekly_bias":weekly,"timeframes":states,"4H_AMD":amd,"daily_location":_location(frames["D"]),
           "contradictions":contradiction["contradictions"],"authority":"W",
           "displacement":latest_disp["strength"] if latest_disp else "NONE",
           "fvg_count":len(fvgs),"order_block_count":len(obs),"source_integrity":source_integrity}
    pattern={"regime":states.get("12M"),"weekly_bias":weekly,"location":state["daily_location"],
             "sweep":bool(sweep_event),"displacement":latest_disp["strength"] if latest_disp else "NONE",
             "choch":bool(shift.get("choch")),"bos":bool(shift.get("bos")),"amd":amd.get("phase")}
    ar=analogue_research(historical_episodes,pattern)
    contradictions=contradiction["contradictions"]
    hypotheses=[
        {"name":"continuation","evidence":[e["claim_id"] for e in evidence],"contradictions":[c["explanation"] for c in contradictions],
         "invalidation":["Weekly structure changes","key liquidity is invalidated"]},
        {"name":"structural_conflict","evidence":[],"contradictions":[c["explanation"] for c in contradictions],
         "invalidation":["conflicting timeframe resolves"]}
    ]
    liquidity={"zones":zones,"sweep":sweep_event,"inducement":inducement,
               "external_zone_count":len(ws),"internal_zone_count":len(ins[-40:])}
    return build_report(symbol,now or df.index[-1],state,liquidity,events,macro,hypotheses,evidence,ar)
