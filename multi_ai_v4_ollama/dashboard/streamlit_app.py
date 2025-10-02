import streamlit as st, json, os

st.set_page_config(page_title="MULTI_AI v4.0", page_icon="🤖", layout="wide")
st.title("🚀 MULTI_AI v4.0 - Ollama Dashboard")

col1, col2 = st.columns([2,1])
with col1:
    st.subheader("📁 Sprint Sonuçları")
    if os.path.exists("sprint_result.json"):
        st.json(json.load(open("sprint_result.json", encoding="utf-8")))
    else:
        st.info("Henüz sprint sonucu yok.")

with col2:
    st.subheader("⚙️ Aksiyonlar")
    st.code("python -m multi_ai_v4_ollama.main")
    st.subheader("📈 Telemetry")
    if os.path.exists("trace_log.jsonl"):
        lines = open("trace_log.jsonl", encoding="utf-8").read().splitlines()[-20:]
        for ln in lines: st.text(ln[:300])
    else:
        st.info("trace_log.jsonl bulunamadı.")
