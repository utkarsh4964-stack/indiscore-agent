# --- STEP 1: SQLITE VERSION HACK (MUST BE FIRST) ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass # Fallback for local environments

import streamlit as st
import subprocess
import sys
import os
import re

# --- STEP 2: FIX FOR Python 3.12 / CrewAI Telemetry ---
# We manually inject 'pkg_resources' into sys.modules so CrewAI doesn't crash
try:
    import pkg_resources
except ImportError:
    try:
        from importlib import metadata
        # Create a mock object to satisfy CrewAI's version checks
        class MockPkgResources:
            def get_distribution(self, name):
                class Dist:
                    version = "0.0.0"
                return Dist()
        sys.modules['pkg_resources'] = MockPkgResources()
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])

# Now safe to import your local files
try:
    from agents import run_assessment
except ImportError as e:
    st.error(f"Failed to import agents.py: {e}")

# --- STEP 3: UI CONFIG ---
st.set_page_config(page_title="IndiScore Pro", page_icon="🏦", layout="wide")

# Initialize Session State
if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0
if 'status_label' not in st.session_state:
    st.session_state.status_label = "PENDING"

st.title("🏦 IndiScore Pro")
st.caption("Agentic Credit Intelligence | Utkarsh Sharma")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.write("System Status: **Active**" if api_key else "System Status: **Waiting for Key**")

# --- MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Transaction Data")
    data_input = st.text_area("Paste logs here:", height=300)
    
    if st.button("🚀 Execute Audit", use_container_width=True):
        if not data_input:
            st.error("Missing data.")
        elif not api_key:
            st.error("Missing API Key.")
        else:
            with st.status("Agents are analyzing...", expanded=True) as status:
                try:
                    report = run_assessment(data_input, api_key)
                    st.session_state.audit_report = report
                    
                    # Extraction
                    score_match = re.search(r'FINAL_SCORE:\s*(\d+)', report)
                    status_match = re.search(r'STATUS:\s*(\w+)', report)
                    
                    st.session_state.final_score = int(score_match.group(1)) if score_match else 600
                    st.session_state.status_label = status_match.group(1).upper() if status_match else "REVIEW"
                    
                    status.update(label="Complete!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Error: {e}")

with col2:
    st.subheader("📊 Results")
    if st.session_state.audit_report:
        c1, c2 = st.columns(2)
        c1.metric("Score", st.session_state.final_score)
        c2.info(f"Status: {st.session_state.status_label}")
        st.markdown(st.session_state.audit_report)
    else:
        st.info("Awaiting execution...")
