import streamlit as st
import plotly.graph_objects as go
import re
from PyPDF2 import PdfReader # New requirement: pip install PyPDF2
from agents import run_assessment

st.set_page_config(page_title="IndiScore Pro | Document AI", page_icon="🏦", layout="wide")

# --- PDF EXTRACTION LOGIC ---
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

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
    st.caption("v2.5 - Document AI Active")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.success("PDF Parser: Online")
    st.info("Agent: Llama 3.3 70B")

st.title("Agentic Credit Intelligence Engine")
st.markdown("##### Bridging the gap for 190M+ Credit-Invisible Indians")

# --- INPUT TABS ---
tab1, tab2 = st.tabs(["📄 Upload Bank Statement (PDF)", "⌨️ Manual Entry"])

with tab1:
    uploaded_file = st.file_uploader("Upload your Bank Statement (PDF)", type="pdf")
    if uploaded_file:
        st.success("PDF Uploaded Successfully!")

with tab2:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        upi_manual = st.text_area("Paste UPI Logs", height=150)
    with col_in2:
        bill_manual = st.text_area("Paste Bill History", height=150)

if st.button("🚀 Analyze Creditworthiness"):
    final_upi_data = ""
    final_bill_data = ""

    # Logic to decide which input to use
    if uploaded_file:
        with st.spinner("Extracting data from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            final_upi_data = pdf_text
            final_bill_data = "Data extracted from PDF. See transaction logs."
    else:
        final_upi_data = upi_manual
        final_bill_data = bill_manual

    if final_upi_data:
        with st.status("🧠 Agents are auditing financial character...", expanded=True) as status:
            report_text = run_assessment(final_upi_data, final_bill_data, api_key)
            current_score = extract_score(report_text)
            status.update(label="✅ Underwriting Complete!", state="complete")
        
        # --- RESULTS ---
        res_col1, res_col2 = st.columns([1, 1.5])
        with res_col1:
            st.plotly_chart(create_gauge(current_score), use_container_width=True)
            st.metric("Risk Status", "Verified" if current_score > 700 else "High Risk")
        with res_col2:
            st.markdown("### 🔍 Underwriter Report")
            st.markdown(report_text)
    else:
        st.warning("Please provide a PDF or manual data.")
