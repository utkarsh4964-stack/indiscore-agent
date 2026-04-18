__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
import re
from agents import run_assessment

# UI Config
st.set_page_config(page_title="IndiScore Pro", page_icon="🏦", layout="wide")

if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0

st.title("🏦 IndiScore Pro: Agentic Credit Audit")

with st.sidebar:
    st.header("⚙️ Config")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.info("Uses Llama 3.3-70B to detect circular trading & fraud.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Financial Data")
    upi_data = st.text_area("Paste UPI Logs:", height=200)
    bill_data = st.text_area("Paste Bill History:", height=150)
    
    if st.button("🚀 Run Audit", use_container_width=True):
        if upi_data and api_key:
            with st.status("Agents are debating...", expanded=True) as status:
                report = run_assessment(upi_data, bill_data, api_key)
                st.session_state.audit_report = report
                
                # Regex extraction
                score_match = re.search(r'FINAL_SCORE:\s*(\d+)', report)
                status_match = re.search(r'STATUS:\s*(\w+)', report)
                
                st.session_state.final_score = int(score_match.group(1)) if score_match else 600
                st.session_state.status_label = status_match.group(1).upper() if status_match else "REVIEW"
                status.update(label="Audit Complete", state="complete")
        else:
            st.error("Provide data and API key.")

with col2:
    st.subheader("📊 Underwriter Report")
    if st.session_state.audit_report:
        c1, c2 = st.columns(2)
        c1.metric("Credit Score", st.session_state.final_score)
        
        status_val = st.session_state.status_label
        if "APPROVED" in status_val:
            c2.success(status_val)
        elif "REVIEW" in status_val:
            c2.warning(status_val)
        else:
            c2.error(status_val)
            
        st.markdown(st.session_state.audit_report)
