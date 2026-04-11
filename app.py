__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import re
import os
from agents import run_assessment

# Set page config for a professional look
st.set_page_config(page_title="IndiScore Pro", page_icon="🏦", layout="wide")

# Initialize session state
if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0
if 'status_label' not in st.session_state:
    st.session_state.status_label = "PENDING"

st.title("🏦 IndiScore Pro: Agentic Credit Underwriting")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password")
    st.info("This tool uses a multi-agent system to analyze financial character beyond traditional credit scores.")

# Main input area
col_in, col_out = st.columns([1, 1])

with col_in:
    st.subheader("📝 Transaction Input")
    data_input = st.text_area("Paste Transaction Logs or Bank Narration:", height=300, 
                              placeholder="01-04: Received ₹50,000 from TCS...")
    
    if st.button("🚀 Run Agentic Audit", use_container_width=True):
        if not data_input:
            st.error("Please provide transaction data first.")
        elif not api_key and not os.environ.get("GROQ_API_KEY"):
            st.error("Please provide a Groq API Key.")
        else:
            with st.status("Agents are analyzing data...", expanded=True) as status:
                st.write("🕵️ Data Integrity Specialist is checking for fraud...")
                # Execution
                result = run_assessment(data_input, api_key)
                
                st.session_state.audit_report = result
                
                # Logic to parse the AI output
                score_match = re.search(r'FINAL_SCORE:\s*(\d+)', result)
                status_match = re.search(r'STATUS:\s*(\w+)', result)
                
                st.session_state.final_score = int(score_match.group(1)) if score_match else 600
                st.session_state.status_label = status_match.group(1).upper() if status_match else "REVIEW"
                
                status.update(label="Audit Complete!", state="complete", expanded=False)

# Results Display
with col_out:
    st.subheader("📊 Underwriter Report")
    
    if st.session_state.audit_report:
        # Display Metric
        s_col1, s_col2 = st.columns(2)
        s_col1.metric("IndiScore", st.session_state.final_score)
        
        # Color-coded Status
        status_val = st.session_state.status_label
        if "APPROVED" in status_val:
            s_col2.success(f"STATUS: {status_val}")
        elif "REVIEW" in status_val:
            s_col2.warning(f"STATUS: {status_val}")
        else:
            s_col2.error(f"STATUS: {status_val}")
            
        st.markdown("#### Reasoning Trace")
        st.markdown(st.session_state.audit_report)
    else:
        st.info("Waiting for data analysis...")
