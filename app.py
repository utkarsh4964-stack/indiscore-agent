# --- MANDATORY BOOTSTRAP (DO NOT MOVE) ---
import sys
from types import ModuleType

# 1. Fix for Python 3.12 / CrewAI 'pkg_resources' crash
try:
    import pkg_resources
except ImportError:
    # Create a dummy module to satisfy CrewAI's internal telemetry
    mock_pkg = ModuleType("pkg_resources")
    class MockDist:
        version = "0.0.0"
        def __getattr__(self, name): return lambda *a, **k: None
    mock_pkg.get_distribution = lambda name: MockDist()
    mock_pkg.iter_entry_points = lambda name: iter([])
    sys.modules["pkg_resources"] = mock_pkg

# 2. Fix for SQLite version (Required for ChromaDB/CrewAI on Streamlit)
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass 

# --- STANDARD IMPORTS ---
import streamlit as st
import os
import re
from agents import run_assessment

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="IndiScore Pro | Agentic Underwriting", 
    page_icon="🏦", 
    layout="wide"
)

# Initialize Session State
if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0
if 'status_label' not in st.session_state:
    st.session_state.status_label = "PENDING"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key", type="password", help="Get your key at console.groq.com")
    st.divider()
    st.markdown("""
    ### System Architecture
    - **Llama 3.3-70B** (Decision Logic)
    - **CrewAI** (Agent Orchestration)
    - **Custom Risk Guardrails**
    """)
    if st.button("Clear Cache"):
        st.session_state.audit_report = None
        st.rerun()

# --- MAIN APP INTERFACE ---
st.title("🏦 IndiScore Pro")
st.caption("Advanced Agentic Credit Risk Assessment Engine")
st.markdown("---")

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("📝 Financial Data Feed")
    upi_input = st.text_area("Paste UPI/Bank Transaction Logs:", height=250, 
                             placeholder="01-04: Received ₹50,000 from TCS...")
    
    bill_input = st.text_area("Paste Utility/Bill History:", height=150,
                              placeholder="March 2026: Electricity ₹2,500 (Paid)...")
    
    if st.button("🚀 Execute Agentic Audit", use_container_width=True):
        if not upi_input:
            st.error("Please provide transaction data.")
        elif not api_key:
            st.error("Please enter your Groq API Key in the sidebar.")
        else:
            with st.status("Agents are analyzing financial character...", expanded=True) as status:
                try:
                    # Execute the CrewAI logic from agents.py
                    report = run_assessment(upi_input, bill_input, api_key)
                    st.session_state.audit_report = report
                    
                    # Extraction Logic
                    score_match = re.search(r'FINAL_SCORE:\s*(\d+)', report)
                    status_match = re.search(r'STATUS:\s*(\w+)', report)
                    
                    st.session_state.final_score = int(score_match.group(1)) if score_match else 600
                    st.session_state.status_label = status_match.group(1).upper() if status_match else "REVIEW"
                    
                    status.update(label="Audit Complete!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
                    status.update(label="Audit Failed", state="error")

with col_out:
    st.subheader("📊 Underwriter Dossier")
    
    if st.session_state.audit_report:
        # Metrics Display
        m1, m2 = st.columns(2)
        m1.metric("IndiScore", st.session_state.final_score)
        
        # Color-coded Decision
        status_text = st.session_state.status_label
        if "APPROVED" in status_text:
            m2.success(f"DECISION: {status_text}")
        elif "REVIEW" in status_text:
            m2.warning(f"DECISION: {status_text}")
        else:
            m2.error(f"DECISION: {status_text}")
            
        st.markdown("#### Reasoning Trace")
        st.info("The agents have cross-referenced income against behavioral markers.")
        st.markdown(st.session_state.audit_report)
    else:
        st.info("Results will appear here once the audit is executed.")

st.divider()
st.caption("Developed by Utkarsh Sharma | B.Tech IT, JSSATE Noida")
