
import json
import time
from pathlib import Path

import streamlit as st

TRACE_FILE = Path(st.session_state.get("trace_file", "trace_log.jsonl"))

st.set_page_config(page_title="Multi-AI Dashboard", layout="wide")

st.title("🧠 Multi-AI Dashboard")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Kontroller")
    tf = st.text_input("Trace Log Yolu", value=str(TRACE_FILE))
    if st.button("Yenile"):
        st.session_state["trace_file"] = tf
        st.rerun()

with col2:
    st.subheader("Canlı İzleme (poll)")
    auto = st.toggle("Otomatik Yenile (2sn)", value=False)

def render():
    tfp = Path(st.session_state.get("trace_file", tf))
    content = []
    if tfp.exists():
        with open(tfp, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    content.append(json.loads(line))
                except Exception:
                    pass
    content = content[-200:]  # son 200 giriş
    st.write(f"Toplam kayıt: {len(content)}")
    for e in reversed(content):
        with st.container(border=True):
            st.markdown(f"**{e.get('timestamp','')} — {e.get('agent','')} — {e.get('status','').upper()} — Task: {e.get('task_id','')}**")
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Input")
                st.code(json.dumps(e.get("input"), ensure_ascii=False, indent=2))
            with c2:
                st.caption("Output")
                st.code(json.dumps(e.get("output"), ensure_ascii=False, indent=2))

placeholder = st.empty()
with placeholder.container():
    render()
    if auto:
        time.sleep(2)
        st.rerun()
