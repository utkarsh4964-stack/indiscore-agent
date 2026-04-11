import subprocess
import sys

# --- STEP 1: BOOTSTRAP FOR PYTHON 3.12 COMPATIBILITY ---
# This must run before 'from agents import ...' or any crewai imports
try:
    import pkg_resources
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    import pkg_resources

# --- STEP 2: SQLITE VERSION HACK ---
# Required because Streamlit Cloud uses an outdated SQLite version incompatible with ChromaDB
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import re
import os
from agents import run_assessment

# --- STEP 3: UI CONFIGURATION ---
st.set_page_config(page_title="IndiScore Pro | AI Underwriting", page_icon="🏦", layout="wide")

# Initialize Session State
if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0
if 'status_label' not in st.session_state:
    st.session_state.status_label = "PENDING"

# --- STEP 4: APP LAYOUT ---
st.title("🏦 IndiScore Pro")
st.caption("Multi-Agent Credit Intelligence Engine powered by Llama 3.3 & CrewAI")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuration")
    # Priority: User Input > Environment Variable
    api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq Cloud API Key")
    st.divider()
    st.markdown("### How it works")
    st.info("""
    1. **Data Integrity Agent**: Checks for fraud/circular trading.
    2. **Risk Auditor**: Analyzes behavioral red flags (gambling, defaults).
    3. **Chief Underwriter**: Synthesizes a final score and status.
    """)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📥 Transaction Feed")
    data_input = st.text_area(
        "Paste Raw Logs or Bank Statement Text:", 
        height=350,
        placeholder="Example: 05-04-2026 Received ₹75,000 from GOOGLE INDIA..."
    )
    
    if st.button("🚀 Run Agentic Audit", use_container_width=True):
        if not data_input:
            st.error("Please provide transaction data.")
        elif not api_key and not os.environ.get("GROQ_API_KEY"):
            st.error("API Key missing! Please provide it in the sidebar.")
        else:
            with st.status("Agents are debating your creditworthiness...", expanded=True) as status:
                st.write("🕵️ Verifying transaction integrity...")
                
                # Execute the CrewAI logic
                try:
                    report = run_assessment(data_input, api_key)
                    st.session_state.audit_report = report
                    
                    # Regex Extraction for Score and Status
                    score_match = re.search(r'FINAL_SCORE:\s*(\d+)', report)
                    status_match = re.search(r'STATUS:\s*(\w+)', report)
                    
                    st.session_state.final_score = int(score_match.group(1)) if score_match else 600
                    st.session_state.status_label = status_match.group(1).upper() if status_match else "REVIEW"
                    
                    status.update(label="Audit Complete!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Audit failed: {e}")
                    status.update(label="Audit Failed", state="error")

with col_right:
    st.subheader("📊 Underwriter Output")
    
    if st.session_state.audit_report:
        # Visualizing the Score
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("IndiScore", st.session_state.final_score, delta_color="normal")
        
        status_text = st.session_state.status_label
        if "APPROVED" in status_text:
            m_col2.success(f"DECISION: {status_text}")
        elif "REVIEW" in status_text:
            m_col2.warning(f"DECISION: {status_text}")
        else:
            m_col2.error(f"DECISION: {status_text}")
            
        st.markdown("### Agent Reasoning Trace")
        st.markdown(st.session_state.audit_report)
    else:
        st.info("Results will appear here once the audit is executed.")

st.markdown("---")
st.caption("Built for HKU Summer Institute & MLH Fellowship Applications | Developed by Utkarsh Sharma")
