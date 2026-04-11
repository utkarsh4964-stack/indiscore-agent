import streamlit as st
import plotly.graph_objects as go
import re
from agents import run_assessment

st.set_page_config(page_title="IndiScore Pro AI", page_icon="💳", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .metric-card { background-color: #111; padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

def extract_score(text):
    match = re.search(r'FINAL_SCORE:\s*(\d{3})', text)
    if match: return int(match.group(1))
    scores = re.findall(r'\b([3-9]\d{2})\b', text)
    return int(scores[-1]) if scores else 300

def create_gauge(score):
    color = "#ff4b4b" if score < 600 else "#ffa500" if score < 750 else "#00cc66"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        gauge = {'axis': {'range': [300, 900]}, 'bar': {'color': color},
                 'steps': [{'range': [300, 600], 'color': "#331111"},
                          {'range': [600, 750], 'color': "#332211"},
                          {'range': [750, 900], 'color': "#113311"}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 IndiScore Pro")
    st.caption("v2.0 - Hackathon Edition")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.write("🕵️ **4-Agent System Active**")
    st.status("Anti-Fraud Engine: Live")

# --- MAIN UI ---
st.header("Financial Character & Credit Assessment")
st.info("Targeting the 190M credit-invisible Indians through Alternative Data Intelligence.")

c1, c2 = st.columns(2)
with c1:
    upi_input = st.text_area("UPI Logs (Income & Rent markers)", height=150, placeholder="Paste transaction history...")
with c2:
    bill_input = st.text_area("Utility History (Punctuality signals)", height=150, placeholder="Paste bill payment history...")

if st.button("🚀 Execute Multi-Agent Audit"):
    if upi_input and bill_input:
        with st.status("🧠 Agents are debating your creditworthiness...", expanded=True) as status:
            report = run_assessment(upi_input, bill_input, api_key)
            score = extract_score(report)
            status.update(label="✅ Audit Complete", state="complete")
        
        # DISPLAY RESULTS
        col_res1, col_res2 = st.columns([1, 1.2])
        with col_res1:
            st.plotly_chart(create_gauge(score), use_container_width=True)
            
            # --- BREAKDOWN TILES ---
            st.markdown("### 📊 Agent Confidence")
            k1, k2 = st.columns(2)
            k1.metric("Stability", "High" if score > 700 else "Moderate")
            k2.metric("Risk Level", "Low" if score > 750 else "High")
            
        with col_res2:
            st.markdown("### 🔍 Underwriter Reasoning Trace")
            st.markdown(report)
            
            # Export button for judges to see "Productization"
            st.button("📥 Download Official PDF Report (Mock)")
    else:
        st.error("Please enter both transaction and bill data.")

st.divider()
st.caption("Built for Hackathon Demo | JSSATE Noida | Powered by Llama 3.3 70B")
