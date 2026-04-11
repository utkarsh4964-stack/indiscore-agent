__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import re
from agents import run_assessment

# Initialize session state for the report
if 'audit_report' not in st.session_state:
    st.session_state.audit_report = None
if 'final_score' not in st.session_state:
    st.session_state.final_score = 0

st.title("🏦 IndiScore Pro v2.0")

# Input section
with st.expander("📝 Input Financial Data", expanded=True):
    data_input = st.text_area("Paste UPI/Bank Logs here:", height=150)
    api_key = st.text_input("Custom Groq Key (Optional)", type="password")

if st.button("🚀 Execute Agentic Audit"):
    if not data_input:
        st.error("Please provide data.")
    else:
        with st.spinner("Agents are debating your creditworthiness..."):
            # Run the Crew
            result = run_assessment(data_input, api_key)
            st.session_state.audit_report = result
            
            # Extract Score & Status via Regex
            score_match = re.search(r'FINAL_SCORE:\s*(\d+)', result)
            status_match = re.search(r'STATUS:\s*(\w+)', result)
            
            st.session_state.final_score = int(score_match.group(1)) if score_match else 600
            st.session_state.status_label = status_match.group(1) if status_match else "REVIEW"

# Display Results from Session State
if st.session_state.audit_report:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Credit Score", st.session_state.final_score)
        
        # Color-coded Status Label
        status = st.session_state.status_label.upper()
        if "APPROVED" in status:
            st.success(f"✅ {status}")
        elif "REVIEW" in status:
            st.warning(f"⚠️ {status}")
        else:
            st.error(f"❌ {status}")
            
    with col2:
        st.markdown("### 🔍 Underwriter Logic")
        st.markdown(st.session_state.audit_report)
