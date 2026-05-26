"""
app.py — IndiScore Pro | Agentic Credit Intelligence Engine
Streamlit front-end for the multi-agent credit scoring pipeline.
"""

import re
import streamlit as st
import plotly.graph_objects as go
from pypdf import PdfReader
from agents import run_assessment

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IndiScore Pro | Credit Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3a3f60;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
    }
    .score-band-poor   { color: #ff4b4b; font-weight: bold; }
    .score-band-fair   { color: #ff8c00; font-weight: bold; }
    .score-band-good   { color: #ffd700; font-weight: bold; }
    .score-band-excel  { color: #00cc66; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    """Extract all text from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        return text
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
        return ""


def extract_score(text: str) -> int:
    """
    Extract the final credit score from the LLM report.
    Primary:  looks for 'FINAL_SCORE: XXX'
    Fallback: last 3-digit number in the valid 300-900 range
    """
    # Primary tag match
    match = re.search(r'FINAL_SCORE:\s*(\d{3})', text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        return max(300, min(900, val))

    # Fallback: any 3-digit number between 300–900
    candidates = [int(x) for x in re.findall(r'\b([3-8]\d{2})\b', text)]
    return candidates[-1] if candidates else 500


def score_band(score: int) -> tuple[str, str, str]:
    """Returns (label, css_class, emoji) for a given score."""
    if score < 550:
        return "Poor", "score-band-poor", "🔴"
    elif score < 650:
        return "Fair", "score-band-fair", "🟠"
    elif score < 750:
        return "Good", "score-band-good", "🟡"
    else:
        return "Excellent", "score-band-excel", "🟢"


def create_gauge(score: int) -> go.Figure:
    """Build an interactive Plotly gauge for the credit score."""
    band_label, _, band_emoji = score_band(score)
    color_map = {
        "Poor": "#ff4b4b",
        "Fair": "#ff8c00",
        "Good": "#ffd700",
        "Excellent": "#00cc66",
    }
    bar_color = color_map[band_label]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={
            "text": f"{band_emoji} {band_label} Credit Profile",
            "font": {"color": "white", "size": 20},
        },
        number={"font": {"color": "white", "size": 56}, "suffix": ""},
        gauge={
            "axis": {
                "range": [300, 900],
                "tickwidth": 1,
                "tickcolor": "#888",
                "tickvals": [300, 400, 500, 600, 700, 800, 900],
            },
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 1,
            "bordercolor": "#444",
            "steps": [
                {"range": [300, 550], "color": "#3a1515"},
                {"range": [550, 650], "color": "#3a2a10"},
                {"range": [650, 750], "color": "#3a3810"},
                {"range": [750, 900], "color": "#0f3a20"},
            ],
            "threshold": {
                "line": {"color": bar_color, "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=300,
        margin=dict(t=50, b=10, l=40, r=40),
    )
    return fig


# ── Demo Data ─────────────────────────────────────────────────────────────────

DEMO_PROFILES = {
    "gig_worker": {
        "label": "🛵 Gig Worker (Good Profile)",
        "upi": """2024-01-05 | ZOMATO_PAYOUT   | +₹4,200
2024-01-08 | SWIGGY_PAYOUT   | +₹3,800
2024-01-12 | ZOMATO_PAYOUT   | +₹3,500
2024-01-15 | Rent_Transfer   | -₹7,000
2024-01-18 | ZOMATO_PAYOUT   | +₹4,100
2024-01-20 | Medical_Store   | -₹650
2024-01-22 | Grocery_BigBazaar | -₹1,200
2024-01-25 | SWIGGY_PAYOUT   | +₹4,500
2024-01-28 | Mobile_Recharge | -₹299
2024-02-05 | ZOMATO_PAYOUT   | +₹5,100
2024-02-10 | SWIGGY_PAYOUT   | +₹4,200
2024-02-15 | Rent_Transfer   | -₹7,000
2024-02-20 | ZOMATO_PAYOUT   | +₹3,900
2024-02-22 | LIC_Premium     | -₹2,500
2024-02-25 | SWIGGY_PAYOUT   | +₹4,800""",
        "bills": "Electricity: Jan✅ Feb✅ Mar✅ Apr✅ | Gas: Jan✅ Feb✅ Mar✅ Apr✅ | Internet: Jan✅ Feb✅ Mar✅ Apr✅ | Water: Jan✅ Feb✅ Mar✅",
    },
    "corporate": {
        "label": "🏢 Corporate Employee (Excellent Profile)",
        "upi": """2024-01-01 | TechCorp_Salary  | +₹85,000
2024-01-05 | Home_Loan_EMI   | -₹22,000
2024-01-10 | SIP_Investment  | -₹10,000
2024-01-15 | Grocery         | -₹3,500
2024-01-20 | Amazon_Purchase | -₹2,100
2024-01-25 | Restaurant      | -₹1,800
2024-02-01 | TechCorp_Salary  | +₹85,000
2024-02-05 | Home_Loan_EMI   | -₹22,000
2024-02-10 | SIP_Investment  | -₹10,000
2024-02-15 | Grocery         | -₹4,200
2024-03-01 | TechCorp_Salary  | +₹85,000
2024-03-05 | Home_Loan_EMI   | -₹22,000""",
        "bills": "Electricity: Jan✅ Feb✅ Mar✅ | Gas: Jan✅ Feb✅ Mar✅ | Internet: Jan✅ Feb✅ Mar✅ | Credit Card: Jan✅ Feb✅",
    },
    "high_risk": {
        "label": "⚠️ High Risk (Poor Profile)",
        "upi": """2024-01-02 | Rahul_Sharma     | +₹10,000
2024-01-02 | Priya_Singh      | -₹9,800
2024-01-05 | Teen_Patti_App   | -₹5,000
2024-01-06 | Rahul_Sharma     | +₹5,200
2024-01-06 | Priya_Singh      | -₹5,100
2024-01-10 | Unknown_Salary   | +₹20,000
2024-01-15 | Rent             | -₹12,000
2024-01-18 | Teen_Patti_App   | -₹8,000
2024-01-20 | Loan_Penalty_Due | -₹3,500
2024-01-25 | Rahul_Sharma     | +₹15,000
2024-01-25 | Priya_Singh      | -₹14,500
2024-01-28 | Paytm_Wallet     | -₹6,000""",
        "bills": "Electricity: Jan❌ Feb✅ Mar❌ Apr✅ (2 late fees) | Gas: Jan❌ Feb❌ Mar✅ (overdue ₹800) | Internet: Jan✅ Feb✅ Mar❌",
    },
}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏦 IndiScore Pro")
    st.caption("v3.0 · Multi-Agent Credit Intelligence")
    st.divider()

    api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get a free key at console.groq.com",
    )

    if api_key:
        st.success("API key entered ✓")
    else:
        st.warning("API key required to run analysis")

    st.divider()

    st.markdown("**🤖 Agent Pipeline**")
    st.markdown("""
1. 📊 Financial Stability Auditor  
2. 🛡️ Fraud & Risk Auditor  
3. 🏦 Chief Credit Underwriter  
""")

    st.divider()

    st.markdown("**🧠 Model**")
    st.info("Llama 3.3 70B via Groq")

    st.divider()

    with st.expander("ℹ️ About IndiScore"):
        st.markdown("""
**IndiScore Pro** helps India's **190M+ credit-invisible** individuals — gig workers, MSME owners, and informal earners — get fair credit access.

It evaluates UPI transactions and utility bills to produce transparent, explainable credit scores.

**Score Bands:**
- 🔴 300–549 Poor
- 🟠 550–649 Fair  
- 🟡 650–749 Good
- 🟢 750–900 Excellent
""")

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🏦 IndiScore Pro")
st.markdown("##### Agentic Credit Intelligence Engine — Bridging the Gap for India's Credit-Invisible Population")

col_h1, col_h2, col_h3, col_h4 = st.columns(4)
col_h1.metric("Population Targeted", "190M+", "credit-invisible")
col_h2.metric("Score Range", "300–900", "transparent")
col_h3.metric("AI Agents", "3", "sequential pipeline")
col_h4.metric("Model", "Llama 3.3 70B", "via Groq")

st.divider()

# ── Input Section ─────────────────────────────────────────────────────────────

st.header("📥 Data Input")

tab_pdf, tab_manual, tab_demo = st.tabs([
    "📄 Upload PDF Bank Statement",
    "⌨️ Manual Text Entry",
    "🧪 Load Demo Profile",
])

# State management for input
if "upi_data" not in st.session_state:
    st.session_state["upi_data"] = ""
if "bill_data" not in st.session_state:
    st.session_state["bill_data"] = ""
if "pdf_file" not in st.session_state:
    st.session_state["pdf_file"] = None

with tab_pdf:
    uploaded_file = st.file_uploader(
        "Upload your Bank Statement or UPI Export (PDF)",
        type=["pdf"],
        help="The PDF will be parsed and all financial data extracted automatically.",
    )
    if uploaded_file:
        st.success(f"✅ **{uploaded_file.name}** uploaded ({uploaded_file.size // 1024} KB)")
        st.session_state["pdf_file"] = uploaded_file
    else:
        st.session_state["pdf_file"] = None

    st.caption("💡 Tip: Export your UPI statement from your bank app or PhonePe/GPay history as a PDF.")

with tab_manual:
    col_a, col_b = st.columns(2)
    with col_a:
        upi_input = st.text_area(
            "💸 UPI Transaction Logs",
            value=st.session_state.get("upi_data", ""),
            height=220,
            placeholder="2024-01-01 | Zomato_Payout | +₹4,200\n2024-01-05 | Rent | -₹8,000\n...",
            key="upi_textarea",
        )
        st.session_state["upi_data"] = upi_input
    with col_b:
        bill_input = st.text_area(
            "🧾 Utility & Bill Payments",
            value=st.session_state.get("bill_data", ""),
            height=220,
            placeholder="Electricity: Jan✅ Feb✅ Mar❌\nGas: Jan✅ Feb✅\nInternet: Jan✅ Feb✅",
            key="bill_textarea",
        )
        st.session_state["bill_data"] = bill_input

with tab_demo:
    st.info("Select a sample profile to instantly populate test data and see the system in action.")
    
    for profile_key, profile in DEMO_PROFILES.items():
        if st.button(f"Load: {profile['label']}", use_container_width=True, key=f"demo_{profile_key}"):
            st.session_state["upi_data"] = profile["upi"]
            st.session_state["bill_data"] = profile["bills"]
            st.session_state["pdf_file"] = None
            st.success(f"✅ Demo profile loaded! Switch to **Manual Text Entry** to see the data, then click Analyze.")
            st.rerun()

# ── Analyze Button ────────────────────────────────────────────────────────────

st.divider()

btn_col, hint_col = st.columns([1, 3])
with btn_col:
    analyze_clicked = st.button(
        "🚀 Analyze Creditworthiness",
        use_container_width=True,
        type="primary",
    )
with hint_col:
    st.caption("⏱️ Analysis runs 3 AI agents sequentially and typically takes 30–90 seconds.")

# ── Run Analysis ──────────────────────────────────────────────────────────────

if analyze_clicked:

    # Validate API key
    if not api_key.strip():
        st.error("⛔ Please enter your Groq API key in the sidebar before running the analysis.")
        st.stop()

    # Determine data source (PDF takes priority)
    final_upi = ""
    final_bills = ""

    if st.session_state.get("pdf_file") is not None:
        with st.spinner("📖 Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(st.session_state["pdf_file"])
        if not pdf_text:
            st.error("❌ Could not extract readable text from this PDF. Try the Manual Entry tab instead.")
            st.stop()
        final_upi = pdf_text
        final_bills = "Financial data extracted from the uploaded PDF document."

    elif st.session_state.get("upi_data", "").strip():
        final_upi = st.session_state["upi_data"]
        final_bills = st.session_state.get("bill_data", "No utility data provided.")

    else:
        st.warning("⚠️ No data provided. Please upload a PDF, enter data manually, or load a demo profile.")
        st.stop()

    # Run multi-agent pipeline
    with st.status("🧠 Multi-Agent Credit Committee is working...", expanded=True) as pipeline_status:
        st.write("**Step 1/3** — 📊 Financial Stability Auditor: analysing income & cashflow patterns...")
        st.write("**Step 2/3** — 🛡️ Fraud & Risk Auditor: scanning for anomalies & red flags...")
        st.write("**Step 3/3** — 🏦 Chief Credit Underwriter: computing final score & report...")
        
        report_text = run_assessment(final_upi, final_bills, api_key)
        score = extract_score(report_text)
        band_label, _, band_emoji = score_band(score)
        
        pipeline_status.update(label=f"✅ Underwriting Complete! Score: {score} ({band_label})", state="complete")

    # ── Financial Stability Analysis Results ──────────────────────────────────

    st.divider()
    st.header("📊 Financial Stability Analysis")

    res_left, res_right = st.columns([1, 1.6], gap="large")

    with res_left:
        st.plotly_chart(create_gauge(score), use_container_width=True)

        st.markdown("#### Score Breakdown")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(
                "Credit Band",
                f"{band_emoji} {band_label}",
                f"{score} / 900",
            )
        with col_m2:
            loan_status = "Eligible ✅" if score >= 650 else "Not Eligible ❌"
            st.metric("Loan Eligibility", loan_status)

        st.markdown("---")
        st.markdown("**Score Reference**")
        st.markdown("""
| Band | Range | Status |
|------|-------|--------|
| 🔴 Poor | 300–549 | High Risk |
| 🟠 Fair | 550–649 | Limited Credit |
| 🟡 Good | 650–749 | Standard Loans |
| 🟢 Excellent | 750–900 | Premium Credit |
""")

    with res_right:
        st.markdown("### 📋 Full Underwriter Report")
        st.markdown("---")
        # Strip the FINAL_SCORE tag from the display (it's shown in the gauge)
        display_report = re.sub(r'\n?FINAL_SCORE:\s*\d+\s*$', '', report_text, flags=re.IGNORECASE).strip()
        st.markdown(display_report)

    # Score history tracking
    if "score_history" not in st.session_state:
        st.session_state["score_history"] = []
    if score not in st.session_state["score_history"]:
        st.session_state["score_history"].append(score)

    # ── Action Buttons ────────────────────────────────────────────────────────

    st.divider()
    st.subheader("📤 Export & Share")

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="⬇️ Download Full Report (.txt)",
            data=f"INDISCORE PRO — CREDIT REPORT\nScore: {score} ({band_label})\n\n{report_text}",
            file_name=f"indiscore_report_{score}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            label="⬇️ Download Report (.md)",
            data=f"# IndiScore Pro — Credit Report\n\n**Score: {score} ({band_label})**\n\n{report_text}",
            file_name=f"indiscore_report_{score}.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    "<div style='text-align:center; color:#666; font-size:0.8rem;'>"
    "🏦 IndiScore Pro · Built for India's Credit-Invisible · Powered by Llama 3.3 70B via Groq"
    "</div>",
    unsafe_allow_html=True,
)
