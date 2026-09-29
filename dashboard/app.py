"""SMC Agent — research-first market intelligence dashboard."""
import pandas as pd
import streamlit as st
from smc_agent.engine import analyze
from smc_agent.timeframes import reconstruct, ANALYSIS_TIMEFRAMES

st.set_page_config(page_title="SMC Intelligence",page_icon="◈",layout="wide",initial_sidebar_state="expanded")

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
<h1>SMC Intelligence</h1><p>Reconstruct structure, investigate liquidity, correlate events, compare historical episodes and challenge hypotheses.</p></div>""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Research input")
    uploaded=st.file_uploader("Upload OHLC CSV",type=["csv"])
    st.caption("Expected: timestamp/time, open, high, low, close. Volume is optional.")
    st.divider()
    st.markdown("### Investigation")
    st.checkbox("Show raw report",value=False,key="raw_report")
    st.caption("Research interface only. No trading or execution.")

if not uploaded:
    st.markdown("### Start an investigation")
    a,b,c=st.columns(3)
    a.markdown(card("Reconstruct","12M → 1M"),unsafe_allow_html=True)
    b.markdown(card("Investigate","Structure + liquidity"),unsafe_allow_html=True)
    c.markdown(card("Challenge","Evidence + contradictions"),unsafe_allow_html=True)
    st.info("Upload a historical OHLC dataset to populate the intelligence workspace.")
    st.stop()

try:
    preview=pd.read_csv(uploaded,nrows=2)
    time_col="timestamp" if "timestamp" in preview.columns else "time" if "time" in preview.columns else None
    if not time_col: st.error("CSV needs a timestamp or time column."); st.stop()
    uploaded.seek(0); df=pd.read_csv(uploaded)
    df[time_col]=pd.to_datetime(df[time_col],utc=True,errors="raise"); df=df.set_index(time_col).sort_index()
    required=["open","high","low","close"]; missing=[x for x in required if x not in df.columns]
    if missing: st.error("Missing OHLC columns: "+", ".join(missing)); st.stop()
    df=df[required+([ "volume"] if "volume" in df.columns else [])].dropna(subset=required)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}"); st.stop()

report=analyze(df).as_dict(); frames=reconstruct(df)
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

overview,structure,liquidity_tab,hypotheses_tab,data_tab=st.tabs(["Overview","Structure","Liquidity & Events","Hypotheses","Research Data"])

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
    st.json(states.get(selected,"NEUTRAL"))

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

with hypotheses_tab:
    st.markdown("### Competing hypotheses")
    if hypotheses:
        for h in hypotheses:
            with st.expander(h.get("name","Hypothesis").replace("_"," ").title(),expanded=True):
                a,b=st.columns(2)
                a.markdown("**Supporting evidence**"); a.write(h.get("evidence",[]) or "None recorded.")
                a.markdown("**Contradictions**"); a.write(h.get("contradictions",[]) or "None recorded.")
                b.markdown("**Invalidation conditions**"); b.write(h.get("invalidation",[]) or "None recorded.")
                b.metric("Research confidence",f"{float(h.get('confidence',0))*100:.0f}%")
    else: st.info("No hypotheses were generated.")

with data_tab:
    st.markdown("### Dataset & research integrity")
    a,b,c,d=st.columns(4)
    a.metric("Source rows",f"{len(df):,}"); b.metric("Source start",df.index.min().strftime("%Y-%m-%d"))
    c.metric("Source end",df.index.max().strftime("%Y-%m-%d")); d.metric("Timeframes",len(frames))
    coverage=pd.DataFrame({"timeframe":list(frames),"bars":[len(frames[x]) for x in frames]})
    st.dataframe(coverage,use_container_width=True,hide_index=True)
    st.caption("Higher-timeframe structure is reconstructed chronologically from the uploaded source timeframe. Research confidence is not predictive accuracy.")

if st.session_state.get("raw_report"):
    st.divider(); st.markdown("### Machine-readable report"); st.json(report)
