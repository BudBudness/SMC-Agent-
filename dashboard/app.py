"""SMC Agent — research-first market intelligence dashboard."""
import sys
from pathlib import Path

# Streamlit Cloud runs this file from dashboard/; expose the repository src package.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd
import streamlit as st
from smc_agent.engine import analyze
from smc_agent.pipeline import run as run_pipeline
from smc_agent.timeframes import reconstruct, ANALYSIS_TIMEFRAMES

st.set_page_config(page_title="Henryz SMC Intelligence",page_icon="◈",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:#080b12}.block-container{max-width:1500px;padding-top:1.2rem}
[data-testid="stSidebar"]{background:#0b0f18;border-right:1px solid rgba(255,255,255,.07)}
.hero{padding:1.1rem 1.25rem;border:1px solid rgba(255,255,255,.08);border-radius:18px;background:linear-gradient(135deg,#1a2230,#0c111b);margin-bottom:1rem}
.eyebrow{color:#8b9bb5;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase}.hero h1{margin:.25rem 0;font-size:2rem}.hero p{color:#9aa8bd;margin:0}
.mtf{padding:.7rem .4rem;border:1px solid rgba(255,255,255,.07);border-radius:14px;text-align:center;background:#0d121d}
.mtf-label{color:#8290a8;font-size:.7rem}.mtf-state{font-weight:700;margin-top:.2rem}.neutral{color:#aeb8c8}.long{color:#78d6b0}.short{color:#f09a9a}
.card{border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:1rem;background:#0d121d;min-height:100px}
.card-label{color:#7f8da5;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em}.card-value{font-size:1.3rem;font-weight:700;margin-top:.35rem}
.event{padding:.7rem .85rem;border-left:3px solid #718096;background:#0d121d;border-radius:0 10px 10px 0;margin-bottom:.45rem}
.event-name{font-weight:650}.event-meta{color:#7f8da5;font-size:.72rem;margin-top:.2rem}.footnote{color:#66748c;font-size:.72rem}
</style>""",unsafe_allow_html=True)

def cls(v): return str(v or "NEUTRAL").lower()
def card(label,value): return f'<div class="card"><div class="card-label">{label}</div><div class="card-value">{value}</div></div>'

st.markdown("""<div class="hero"><div class="eyebrow">Market intelligence · research workspace</div>
<h1>Henryz SMC Intelligence</h1><p>Reconstruct structure, investigate liquidity, correlate events, compare historical episodes and challenge hypotheses.</p></div>""",unsafe_allow_html=True)

@st.cache_data(show_spinner=False, max_entries=2)
def load_research_dataset():
    """Load the dashboard-sized research release without downloading the full archive."""
    import gzip
    from urllib.request import urlopen

    url = "https://github.com/BudBudness/SMC-Agent-/releases/download/research-data/EURUSD_M1_dashboard.csv.gz"
    with urlopen(url, timeout=60) as response:
        with gzip.GzipFile(fileobj=response) as gz:
            frame = pd.read_csv(
                gz,
                usecols=["timestamp", "open", "high", "low", "close", "volume"],
            )

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    frame = frame.drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    required = ["open", "high", "low", "close"]
    frame = frame[required + (["volume"] if "volume" in frame.columns else [])].dropna(subset=required)
    frame.attrs["source_rows"] = len(frame)
    frame.attrs["source_start"] = frame.index.min().isoformat()
    frame.attrs["source_end"] = frame.index.max().isoformat()
    frame.attrs["analysis_window"] = "latest dashboard research window"
    return frame

@st.cache_data(show_spinner=False, max_entries=2)
def load_full_history_mtf():
    import gzip, json
    from urllib.request import urlopen

    url = "https://github.com/BudBudness/SMC-Agent-/releases/download/research-data/EURUSD_MTF_dashboard.json.gz"
    with urlopen(url, timeout=60) as response:
        with gzip.GzipFile(fileobj=response) as gz:
            payload = json.loads(gz.read().decode("utf-8"))
    frames = {}
    for tf, meta in payload["timeframes"].items():
        rows = meta.get("ohlc_tail", [])
        frame = pd.DataFrame(rows, columns=["timestamp","open","high","low","close"])
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        frames[tf] = frame.set_index("timestamp")[["open","high","low","close"]]
    return payload, frames

def load_uploaded(uploaded):
    preview=pd.read_csv(uploaded,nrows=2)
    time_col="timestamp" if "timestamp" in preview.columns else "time" if "time" in preview.columns else None
    if not time_col: raise ValueError("CSV needs a timestamp or time column.")
    uploaded.seek(0); frame=pd.read_csv(uploaded)
    frame[time_col]=pd.to_datetime(frame[time_col],utc=True,errors="raise")
    frame=frame.set_index(time_col).sort_index()
    required=["open","high","low","close"]; missing=[x for x in required if x not in frame.columns]
    if missing: raise ValueError("Missing OHLC columns: "+", ".join(missing))
    return frame[required+([ "volume"] if "volume" in frame.columns else [])].dropna(subset=required)

with st.sidebar:
    st.markdown("### Research input")
    source=st.radio("Dataset",["EUR/USD long history","Upload CSV"],index=0)
    uploaded=st.file_uploader("Upload OHLC CSV",type=["csv"]) if source=="Upload CSV" else None
    if source=="Upload CSV":
        st.caption("Expected: timestamp/time, open, high, low, close. Volume is optional.")
    else:
        st.caption("Persistent EUR/USD research dataset · 2003 → latest validated run")
    st.divider()
    st.markdown("### Investigation")
    st.checkbox("Show raw report",value=False,key="raw_report")
    st.caption("Research interface only. No trading or execution.")

if source=="EUR/USD long history":
    try:
        df=load_research_dataset()
        try:
            mtf_payload, mtf_frames = load_full_history_mtf()
        except Exception as exc:
            st.error("The full-history MTF research artifact could not be loaded.")
            st.caption(str(exc))
            st.stop()
    except Exception as exc:
        st.error("The persistent EUR/USD research dataset could not be loaded.")
        st.caption(str(exc))
        st.stop()
elif not uploaded:
    st.markdown("### Start an investigation")
    a,b,c=st.columns(3)
    a.markdown(card("Reconstruct","12M → 1M"),unsafe_allow_html=True)
    b.markdown(card("Investigate","Structure + liquidity"),unsafe_allow_html=True)
    c.markdown(card("Challenge","Evidence + contradictions"),unsafe_allow_html=True)
    st.info("Choose EUR/USD long history, or upload a historical OHLC dataset.")
    st.stop()
else:
    try:
        df=load_uploaded(uploaded)
    except Exception as exc:
        st.error(f"Could not read the dataset: {exc}"); st.stop()

with st.spinner("Building the market-intelligence workspace…"):
    try:
        pipeline_result = run_pipeline(df)
        report = pipeline_result["report"]
        frames = reconstruct(df)
        if source=="EUR/USD long history":
            frames = mtf_frames
            full_states = {tf: meta["state"] for tf, meta in mtf_payload["timeframes"].items()}
            state0 = report.get("market_state", {})
            state0["timeframes"] = full_states
            state0["weekly_bias"] = full_states.get("W", "NEUTRAL")
            state0["contradictions"] = mtf_payload.get("contradictions", [])
            state0["authority"] = "W"
            report["market_state"] = state0
            report["conclusion"] = ("Structural conflict remains unresolved across timeframes." if mtf_payload.get("contradictions") else "No higher-timeframe structural contradiction is present in the validated MTF state.")
    except Exception as exc:
        st.error("The research engine could not build the dashboard state.")
        st.exception(exc)
        st.stop()
state=report.get("market_state",{}); states=state.get("timeframes",{})
contradictions=state.get("contradictions",[]); events=report.get("events",[])
hypotheses=report.get("hypotheses",[]); liquidity=report.get("liquidity",{})

st.markdown("### Multi-timeframe structure")
cols=st.columns(len(ANALYSIS_TIMEFRAMES))
for col,tf in zip(cols,ANALYSIS_TIMEFRAMES):
    value=states.get(tf,"NEUTRAL")
    col.markdown(f'<div class="mtf"><div class="mtf-label">{tf}</div><div class="mtf-state {cls(value)}">{value}</div></div>',unsafe_allow_html=True)

st.write("")
m1,m2,m3,m4=st.columns(4)
m1.markdown(card("Weekly structure",state.get("weekly_bias","NEUTRAL")),unsafe_allow_html=True)
m2.markdown(card("Contradictions",len(contradictions)),unsafe_allow_html=True)
m3.markdown(card("Detected events",len(events)),unsafe_allow_html=True)
m4.markdown(card("Hypotheses",len(hypotheses)),unsafe_allow_html=True)

overview,structure,liquidity_tab,macro_tab,analogue_tab,hypotheses_tab,evidence_tab,data_tab=st.tabs(["Overview","Structure","Liquidity & Events","Macro Context","Historical Analogues","Hypotheses","Evidence","Research Data"])

with overview:
    left,right=st.columns([1.65,1])
    with left:
        st.markdown("### Price investigation")
        selected_tf=st.selectbox("Timeframe",list(ANALYSIS_TIMEFRAMES),index=3)
        frame=frames[selected_tf]
        st.line_chart(frame[["close"]].tail(500),height=360,use_container_width=True)
        st.caption(f"{selected_tf} · {len(frame):,} bars · {frame.index.min()} → {frame.index.max()}")
    with right:
        st.markdown("### Intelligence conclusion"); st.write(report.get("conclusion","No conclusion available."))
        st.markdown("### Current context")
        st.write(f"**4H AMD:** {state.get('4H_AMD','UNKNOWN')}")
        st.write(f"**Daily location:** {state.get('daily_location','UNKNOWN')}")
        st.write(f"**Displacement:** {state.get('displacement','NONE')}")
        st.write(f"**FVG count:** {state.get('fvg_count',0):,}")
        st.write(f"**Order blocks:** {state.get('order_block_count',0):,}")

with structure:
    st.markdown("### Structural investigation")
    selected=st.selectbox("Inspect timeframe",list(ANALYSIS_TIMEFRAMES),key="structure_tf")
    sf=frames[selected]; x,y,z=st.columns(3)
    x.metric("Bars",f"{len(sf):,}"); y.metric("Start",sf.index.min().strftime("%Y-%m-%d")); z.metric("End",sf.index.max().strftime("%Y-%m-%d"))
    st.line_chart(sf[["close"]].tail(1000),height=420,use_container_width=True)
    selected_state = states.get(selected, "NEUTRAL")
    st.write(selected_state)

with liquidity_tab:
    lcol,ecol=st.columns([1,1.35])
    with lcol:
        st.markdown("### Liquidity map")
        zones=liquidity.get("zones",[])
        if zones: st.dataframe(pd.DataFrame(zones),use_container_width=True,hide_index=True)
        else: st.info("No liquidity zones were produced.")
        if liquidity.get("sweep"): st.markdown("### Latest sweep"); st.json(liquidity["sweep"])
    with ecol:
        st.markdown("### SMC events")
        if events:
            for event in events:
                st.markdown(f'<div class="event"><div class="event-name">{event.get("name","event").upper()}</div><div class="event-meta">{event.get("timeframe","")} · {event.get("kind","")}</div></div>',unsafe_allow_html=True)
        else: st.info("No SMC events were detected.")

with macro_tab:\n    st.markdown("### Macro context")\n    macro=report.get("macro",{}) or {}\n    if macro: st.json(macro)\n    else: st.info("No macro events supplied.")\n\nwith analogue_tab:\n    st.markdown("### Historical analogue research")\n    st.caption("Analogue matching requires a labelled historical episode set; current dashboard displays available event-study evidence without ranking outcomes.")\n    reaction=(report.get("macro",{}) or {}).get("event_reaction_study",{})\n    st.json({"event_study_summary":reaction})\n\nwith hypotheses_tab:
    st.markdown("### Competing hypotheses")
    if hypotheses:
        for h in hypotheses:
            with st.expander(h.get("name","Hypothesis").replace("_"," ").title(),expanded=True):
                a,b=st.columns(2)
                a.markdown("**Supporting evidence**"); a.write(h.get("evidence",[]) or "None recorded.")
                a.markdown("**Contradictions**"); a.write(h.get("contradictions",[]) or "None recorded.")
                b.markdown("**Invalidation conditions**"); b.write(h.get("invalidation",[]) or "None recorded.")
                b.metric("Evidence items",len(h.get("evidence",[]) or []))
    else: st.info("No hypotheses were generated.")

with evidence_tab:\n    st.markdown("### Evidence ledger")\n    evidence=[]\n    for event in events:\n        evidence.append({"claim_id":event.get("name"),"observation":event.get("kind"),"source":event.get("timeframe"),"timestamp":event.get("time"),"method":"research event detector"})\n    if evidence: st.dataframe(pd.DataFrame(evidence),use_container_width=True,hide_index=True)\n    else: st.info("No evidence records available.")\n\nwith data_tab:
    st.markdown("### Dataset & research integrity")
    a,b,c,d=st.columns(4)
    full_rows = mtf_payload["source_rows"] if source=="EUR/USD long history" else df.attrs.get("source_rows", len(df))
    full_start = mtf_payload["source_start"] if source=="EUR/USD long history" else df.attrs.get("source_start", df.index.min().isoformat())
    full_end = mtf_payload["source_end"] if source=="EUR/USD long history" else df.attrs.get("source_end", df.index.max().isoformat())
    a.metric("Analysis rows",f"{len(df):,}"); b.metric("Full source rows",f"{full_rows:,}")
    c.metric("Source range",f"{full_start[:10]} → {full_end[:10]}"); d.metric("Timeframes",len(frames))
    if source=="EUR/USD long history":
        coverage=pd.DataFrame({"timeframe":list(mtf_payload["timeframes"]), "full_history_bars":[mtf_payload["timeframes"][x]["bars"] for x in mtf_payload["timeframes"]], "visualization_bars":[len(frames[x]) for x in mtf_payload["timeframes"]]})
        st.dataframe(coverage,use_container_width=True,hide_index=True)
        st.caption("Higher-timeframe states come from the full validated EUR/USD history. Charts use bounded recent OHLC tails from the same full-history reconstruction. Recent M1 analysis remains a separate microstructure window.")
    else:
        coverage=pd.DataFrame({"timeframe":list(frames),"bars":[len(frames[x]) for x in frames]})
        st.dataframe(coverage,use_container_width=True,hide_index=True)
        st.caption("Uploaded data is reconstructed from the supplied dataset. Evidence counts describe recorded evidence, not predictive accuracy.")

if st.session_state.get("raw_report"):
    st.divider(); st.markdown("### Machine-readable report"); st.json(report)
