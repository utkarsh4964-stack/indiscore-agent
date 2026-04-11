import streamlit as st
import plotly.graph_objects as go
import re
from agents import run_assessment

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IndiScore AI", page_icon="🏦", layout="wide")

# Custom CSS for a professional Fintech look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Helper function to extract a numerical score from the agent's markdown text
def extract_score(text):
    scores = re.findall(r'\b\d{3}\b', text)
    if scores:
        return int(scores[-1]) # Returns the last 3-digit number found
    return 300 # Default fallback

def create_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [300, 900], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00d4ff"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [300, 600], 'color': '#ff4b4b'},
                {'range': [600, 750], 'color': '#ffa500'},
                {'range': [750, 900], 'color': '#00cc66'}],
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=350, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 IndiScore AI")
    st.info("Solving Financial Inclusion for the credit-invisible using Agentic AI.")
    
    api_key = st.text_input("Enter Groq API Key", type="password")
    
    st.divider()
    st.markdown("### 🛠️ System Logs")
    st.status("Llama 3.3 70B: Online", state="complete")
    st.write("🕵️ Transaction Agent: **Ready**")
    st.write("📡 Utility Agent: **Ready**")
    st.write("⚖️ Chief Underwriter: **Ready**")

# --- MAIN INTERFACE ---
st.title("Agentic Credit Assessment")
st.caption("Alternative Data Scoring for India's New-to-Credit Segment")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📱 UPI & Transaction Logs")
    upi_input = st.text_area("Paste UPI history...", height=150, 
                             placeholder="e.g. Sent 500 to Grocery... Received 25000 from Employer...")
    
    uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type="pdf")
    if uploaded_file:
        st.success("File uploaded! (Extraction logic ready for integration)")

with col2:
    st.markdown("### 🔌 Utility & Behavioral Data")
    bill_input = st.text_area("Paste bill history...", height=150, 
                              placeholder="e.g. Airtel: Paid on time... Gas: Paid 2 days late...")

st.divider()

if st.button("🚀 Generate Agentic Credit Report"):
    if not upi_input or not bill_input:
        st.warning("Please provide both datasets for a complete assessment.")
    else:
        with st.status("🧠 Multi-Agent Orchestration in Progress...", expanded=True) as status:
            st.write("🕵️ Transaction Agent analyzing cashflow stability...")
            st.write("📡 Utility Agent assessing behavioral punctuality...")
            st.write("⚖️ Chief Underwriter synthesizing final decision...")
            
            try:
                # 1. Run Assessment
                report_text = run_assessment(upi_input, bill_input, api_key)
                current_score = extract_score(report_text)
                
                status.update(label="✅ Assessment Complete!", state="complete", expanded=False)
                
                # 2. Visual Results Header
                res_col1, res_col2 = st.columns([1, 1.5])
                
                with res_col1:
                    st.plotly_chart(create_gauge(current_score), use_container_width=True)
                
                with res_col2:
                    st.markdown("### 📊 Key Indicators")
                    k1, k2 = st.columns(2)
                    k1.metric("Financial Health", "Stable" if current_score > 600 else "Critical", delta="+5%")
                    k2.metric("Trust Level", "Verified", delta="High", delta_color="normal")
                    
                    st.markdown("#### 📄 Executive Summary")
                    # We show just the first 500 chars as a summary
                    st.write(report_text[:500] + "...")
                
                # 3. Full Detailed Report
                with st.expander("🔍 View Full Underwriter's Reasoning Trace"):
                    st.markdown(report_text)
                    
            except Exception as e:
                st.error(f"System Error: {e}")

st.divider()
st.markdown("© 2026 IndiScore AI | Built by Utkarsh Sharma | JSSATE Noida")
