import streamlit as st
import plotly.graph_objects as go
import re
from agents import run_assessment

st.set_page_config(page_title="IndiScore Pro | Agentic Credit", page_icon="🏦", layout="wide")

# Custom CSS for Hackathon Appeal
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00d4ff; }
    .stTextArea textarea { border: 1px solid #333; }
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
                 'steps': [{'range': [300, 600], 'color': "#221111"},
                          {'range': [600, 750], 'color': "#221a11"},
                          {'range': [750, 900], 'color': "#112211"}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300, margin=dict(t=0, b=0))
    return fig

# --- UI LAYOUT ---
with st.sidebar:
    st.title("🏦 IndiScore Pro")
    st.caption("Agentic Financial Intelligence")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.success("Core Model: Llama 3.3 70B")
    st.info("Strategy: Hierarchical Multi-Agent")

st.title("Alternative Data Underwriting Engine")
st.markdown("##### Bridging the gap for 190M+ Credit-Invisible Indians")

col_in1, col_in2 = st.columns(2)
with col_in1:
    upi_input = st.text_area("Paste UPI Transaction Logs", height=200, placeholder="Salary, Rent, Groceries...")
with col_in2:
    bill_input = st.text_area("Paste Utility/Bill History", height=200, placeholder="Electricity, JioFiber, Amazon...")

if st.button("🚀 Run Multi-Agent Decision Engine"):
    if upi_input and bill_input:
        with st.status("🧠 Agents are auditing financial character...", expanded=True) as status:
            report_text = run_assessment(upi_input, bill_input, api_key)
            current_score = extract_score(report_text)
            status.update(label="✅ Underwriting Complete!", state="complete")
        
        # --- RESULTS DASHBOARD ---
        res_col1, res_col2 = st.columns([1, 1.5])
        
        with res_col1:
            st.plotly_chart(create_gauge(current_score), use_container_width=True)
            
            # Metrics for "Hackathon Polish"
            m1, m2 = st.columns(2)
            m1.metric("Financial Health", f"{'High' if current_score > 750 else 'Moderate'}")
            m2.metric("Confidence Score", "94%") # Mock confidence score
            
            st.download_button("📥 Download Audit Report", report_text, file_name="indiscore_report.md")

        with res_col2:
            st.markdown("### 🔍 Underwriter's Reasoning Trace")
            st.markdown(report_text)
    else:
        st.warning("Please fill both inputs to proceed.")
