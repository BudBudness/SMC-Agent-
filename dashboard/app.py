import streamlit as st,pandas as pd
from smc_agent.engine import analyze
st.set_page_config(page_title="SMC Agent",layout="wide")
st.title("SMC Agent — Market Intelligence")
st.caption("Investigation interface. No trading or execution.")
up=st.file_uploader("Upload OHLC CSV",type=["csv"])
if up:
    col="timestamp" if "timestamp" in pd.read_csv(up,nrows=1).columns else "time"
    up.seek(0); df=pd.read_csv(up); df[col]=pd.to_datetime(df[col],utc=True); df=df.set_index(col)[["open","high","low","close"]]
    a=analyze(df).as_dict()
    c=st.columns(4)
    c[0].metric("Weekly",str(a["market_state"].get("weekly_bias")))
    c[1].metric("Contradictions",len(a["market_state"].get("contradictions",[])))
    c[2].metric("Events",len(a["events"]))
    c[3].metric("Hypotheses",len(a["hypotheses"]))
    st.subheader("Conclusion"); st.write(a["conclusion"])
    st.subheader("Intelligence report"); st.json(a)
