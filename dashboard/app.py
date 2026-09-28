import streamlit as st,pandas as pd
from smc_agent.engine import analyze
st.set_page_config(page_title="SMC Agent",layout="wide"); st.title("SMC Agent — Macro → Micro"); st.caption("Research / paper dashboard. Live execution is disabled.")
up=st.file_uploader("Upload OHLC CSV",type=["csv"])
if up:
 df=pd.read_csv(up,parse_dates=["timestamp"]).set_index("timestamp"); a=analyze(df).as_dict()
 c=st.columns(4); c[0].metric("Weekly",str(a["weekly_bias"])); c[1].metric("Score",a["score"]); c[2].metric("Grade",a["grade"]); c[3].metric("Status",a["status"]); st.json(a)
