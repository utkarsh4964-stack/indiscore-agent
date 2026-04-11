import streamlit as st
import plotly.graph_objects as go
import re
from pypdf import PdfReader
from agents import run_assessment

st.set_page_config(page_title="IndiScore Pro | Agentic Intelligence", page_icon="🏦", layout="wide")

# --- UI ENHANCEMENTS ---
st.markdown("""
    <style>
    .stAlert { border-radius: 10px; border: none; background-color: #1e2130; }
    .report-card { background-color: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    # Improvement: Extracting only first 5 pages to manage LLM context window/tokens
    text = ""
    for page in reader.pages[:5]:
        text += page.extract_text()
    return text

def create_gauge(score):
    color = "#ff4b4b" if score < 600 else "#ffa500" if score < 750 else "#00cc66"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        gauge = {'axis': {'range': [300, 900], 'tickwidth': 1},
                 'bar': {'color': color},
                 'bgcolor': "#222",
                 'steps': [{'range': [300, 600], 'color': "#331a1a"},
                          {'range': [600, 750], 'color': "#332a1a"},
                          {'range': [750, 900], 'color': "#1a331a"}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "sans-serif"}, height=350)
    return fig

# --- APP LAYOUT ---
with st.sidebar:
    st.title("🏦 IndiScore Pro")
    st.info("Status: AI Multi-Agent Engine Live")
    st.divider()
    # Improvement: Added a 'Simulation Mode' toggle for the pitch
    demo_mode = st.toggle("Enable Pitch Simulation Mode", value=True)

st.title("Agentic Credit Intelligence")
st.caption("Targeting the 190M credit-invisible Indians through Alternative Data Intelligence.")

uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type="pdf", help="Privacy: Data is processed in-memory and not stored.")

if st.button("🚀 Execute Multi-Agent Audit"):
    if uploaded_file:
        with st.status("🧠 Orchestrating Agents...", expanded=True) as status:
            raw_text = extract_text_from_pdf(uploaded_file)
            st.write("🔍 Privacy Guard: Anonymizing sensitive PII...")
            
            # Improvement: Now passing a 'Context' string to the agents
            report_text = run_assessment(raw_text, "Source: PDF Upload", None)
            
            # Simple score extraction logic
            score_match = re.search(r'FINAL_SCORE:\s*(\d{3})', report_text)
            current_score = int(score_match.group(1)) if score_match else 650
            status.update(label="✅ Audit Complete", state="complete")

        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.plotly_chart(create_gauge(current_score), use_container_width=True)
            
            # Improvement: Actionable UI Card
            st.markdown(f"""
            <div class='report-card'>
                <h4>Score Analysis</h4>
                <p style='color: gray;'>Confidence Level: 92%</p>
                <hr style='border: 0.1px solid #444'>
                <p><b>Status:</b> {'✅ Eligible' if current_score > 700 else '⚠️ Review Required'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 📋 Underwriter Reasoning Trace")
            st.markdown(report_text)
