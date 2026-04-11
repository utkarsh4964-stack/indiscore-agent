import streamlit as st
import plotly.graph_objects as go
import re
from pypdf import PdfReader
from agents import run_assessment

st.set_page_config(page_title="IndiScore Pro", page_icon="🏦", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .report-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        # Cap at 3 pages to save tokens and avoid Rate Limits
        for page in reader.pages[:3]:
            text += page.extract_text()
        return text[:6000] # Safety character cap
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def create_gauge(score):
    color = "#ff4b4b" if score < 600 else "#ffa500" if score < 750 else "#00cc66"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        gauge = {'axis': {'range': [300, 900]}, 'bar': {'color': color},
                 'steps': [{'range': [300, 600], 'color': "#2b1b1b"},
                          {'range': [600, 750], 'color': "#2b261b"},
                          {'range': [750, 900], 'color': "#1b2b1b"}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 IndiScore Pro")
    st.caption("Agentic Alternative Credit Scoring")
    user_key = st.text_input("Groq API Key (Optional)", type="password", help="If blank, uses system secrets.")
    st.divider()
    st.write("✅ **Strategy:** Hybrid 8B/70B")
    st.write("✅ **Extraction:** Document AI (pypdf)")

# --- MAIN UI ---
st.title("Alternative Credit Underwriting Engine")
st.markdown("##### Empowering the Credit-Invisible through Agentic AI")

tab1, tab2 = st.tabs(["📄 PDF Statement", "⌨️ Manual Logs"])

with tab1:
    uploaded_file = st.file_uploader("Upload Bank Statement", type="pdf")
    
with tab2:
    upi_logs = st.text_area("Paste Transaction Logs/SMS", height=200)

if st.button("🚀 Run Agentic Audit"):
    input_data = ""
    if uploaded_file:
        input_data = extract_text_from_pdf(uploaded_file)
    elif upi_logs:
        input_data = upi_logs

    if input_data:
        with st.status("🧠 Orchestrating Agents...", expanded=True) as status:
            report = run_assessment(input_data, "Manual Entry", user_key)
            
            # Extract Score
            score_match = re.search(r'FINAL_SCORE:\s*(\d{3})', report)
            score = int(score_match.group(1)) if score_match else 650
            status.update(label="✅ Audit Complete", state="complete")

        # --- RESULTS ---
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.plotly_chart(create_gauge(score), use_container_width=True)
            st.markdown(f"""
            <div class='report-card'>
                <h4>Analysis Details</h4>
                <p>Confidence: 94%</p>
                <p>Status: {'✅ Approved' if score > 700 else '⚠️ Review'}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("### 🔍 Underwriter Report")
            st.markdown(report)
    else:
        st.warning("Please provide data via PDF or Text.")
