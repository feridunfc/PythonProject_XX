import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Meta AI Orchestrator", layout="wide")
st.title("🏭 Meta AI Orchestrator – Dashboard (MVP)")

st.sidebar.header("Filters")
svc = st.sidebar.text_input("Service", "pythonproject_xx")
budget = st.sidebar.number_input("Monthly Limit (USD)", min_value=0.0, value=50.0)

st.subheader("Recent Traces (trace_log.jsonl)")
try:
    df = pd.read_json("trace_log.jsonl", lines=True)
    st.dataframe(df.tail(200), use_container_width=True)
except Exception as e:
    st.info("trace_log.jsonl bulunamadı.")

st.subheader("Cost Guard (snapshot)")
try:
    import utils.cost_guard as cg
    used = cg.spend(0.0)  # sadece okumak için 0 ekliyoruz
    st.metric("Used this month", f"${used:.2f}", delta=None)
except Exception as e:
    st.warning(str(e))