import streamlit as st
import plotly.graph_objects as go
from agents import run_assessment

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IndiScore AI", page_icon="🏦", layout="wide")

# Custom CSS for a professional Fintech look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #00d4ff; color: black; font-weight: bold; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

def create_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [300, 900], 'tickwidth': 1},
            'bar': {'color': "#00d4ff"},
            'steps': [
                {'range': [300, 550], 'color': "#ff4b4b"},
                {'range': [550, 750], 'color': "#ffa500"},
                {'range': [750, 900], 'color': "#00cc66"}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=300)
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 IndiScore AI")
    st.info("Transforming Financial Inclusion for 190M credit-invisible Indians via Multi-Agent AI.")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.divider()
    st.markdown("### 🛠️ Agent Status")
    st.write("🕵️ Transaction Agent: **Standby**")
    st.write("📡 Utility Agent: **Standby**")

# --- MAIN INTERFACE ---
st.title("Agentic Credit Assessment")
st.caption("Powered by Llama 3.3 70B & CrewAI")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📱 UPI & Transaction Logs")
    upi_input = st.text_area("Paste UPI messages or bank alerts here...", height=200, 
                             placeholder="e.g. Sent Rs. 500 to Mom... Received Rs. 45,000 from Zomato...")
    uploaded_pdf = st.file_uploader("Or upload Bank Statement (Coming Soon)", type="pdf")

with col2:
    st.markdown("### 🔌 Utility & Behavioral Data")
    bill_input = st.text_area("Paste bill payment history here...", height=200, 
                              placeholder="e.g. Jio Recharge: Successful... Electricity Bill: Paid on 2nd March...")

if st.button("🚀 Run Multi-Agent Scoring"):
    if not upi_input or not bill_input:
        st.error("Please provide both Transaction and Utility data.")
    else:
        with st.status("🧠 Agents are deliberating...", expanded=True) as status:
            st.write("🕵️ Scanning UPI patterns for stability...")
            st.write("📡 Analyzing bill punctuality...")
            st.write("⚖️ Manager Agent reconciling conflicts...")
            
            try:
                # Run the backend
                report = run_assessment(upi_input, bill_input, api_key)
                status.update(label="✅ Assessment Complete!", state="complete", expanded=False)
                
                # --- RESULTS DISPLAY ---
                st.divider()
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    # Mock extraction of score for the Gauge (assuming report contains a number)
                    # In a real app, you'd regex this out. For demo, we use 715.
                    st.plotly_chart(create_gauge(715), use_container_width=True)
                
                with res_col2:
                    st.markdown("### 📄 Underwriter's Report")
                    st.markdown(report)
                    
            except Exception as e:
                st.error(f"Orchestration Error: {e}")

st.divider()
st.caption("IndiScore v1.2 | Built by Utkarsh Sharma | JSSATE Noida 2026")
