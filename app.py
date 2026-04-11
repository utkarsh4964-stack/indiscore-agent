import streamlit as st
import plotly.graph_objects as go
import re
from agents import run_assessment

# --- UI CONFIGURATION ---
st.set_page_config(page_title="IndiScore AI", page_icon="🏦", layout="wide")

def extract_score(text):
    # 1. Try to find the specific anchor tag first
    match = re.search(r'FINAL_SCORE:\s*(\d{3})', text)
    if match:
        return int(match.group(1))
    
    # 2. Fallback: Find any 3-digit number between 300 and 900
    scores = re.findall(r'\b([3-9]\d{2})\b', text)
    if scores:
        return int(scores[-1]) # Take the last one (usually the summary score)
    
    return 300 # Default if all else fails

def create_gauge(score):
    # Dynamic color based on score
    color = "#ff4b4b" if score < 600 else "#ffa500" if score < 750 else "#00cc66"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        gauge = {
            'axis': {'range': [300, 900]},
            'bar': {'color': color},
            'steps': [
                {'range': [300, 600], 'color': "rgba(255, 75, 75, 0.1)"},
                {'range': [600, 750], 'color': "rgba(255, 165, 0, 0.1)"},
                {'range': [750, 900], 'color': "rgba(0, 204, 102, 0.1)"}]
        }))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 IndiScore AI")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.divider()
    st.status("Llama 3.3 70B: Online")
    st.write("🕵️ Transaction Agent: **Ready**")
    st.write("📡 Utility Agent: **Ready**")

# --- MAIN UI ---
st.title("Agentic Credit Assessment")
col1, col2 = st.columns(2)

with col1:
    upi_input = st.text_area("Paste UPI history...", height=150)
with col2:
    bill_input = st.text_area("Paste bill history...", height=150)

if st.button("🚀 Run Multi-Agent Scoring"):
    if upi_input and bill_input:
        with st.status("🧠 Agents are thinking...", expanded=True) as status:
            report_text = run_assessment(upi_input, bill_input, api_key)
            current_score = extract_score(report_text)
            status.update(label="✅ Assessment Complete!", state="complete")
        
        # Display Results
        res_col1, res_col2 = st.columns([1, 1.5])
        with res_col1:
            st.plotly_chart(create_gauge(current_score), use_container_width=True)
        with res_col2:
            st.markdown("### 📄 Underwriter Report")
            st.markdown(report_text)
    else:
        st.warning("Please fill both inputs.")
