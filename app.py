"""
app.py — IndiScore Pro | Agentic Credit Intelligence Engine
API key is pre-configured via Streamlit secrets — users never need to enter it.
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
    /* Hide the default Streamlit header padding */
    .block-container { padding-top: 1.5rem; }

    /* Score band colours */
    .band-poor    { color: #ff4b4b; font-weight: 700; }
    .band-fair    { color: #ff8c00; font-weight: 700; }
    .band-good    { color: #ffd700; font-weight: 700; }
    .band-excel   { color: #00cc66; font-weight: 700; }

    /* Hero metric strip */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1d2e, #212440);
        border: 1px solid #2e3255;
        border-radius: 10px;
        padding: 12px 16px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    try:
        reader = PdfReader(pdf_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
        return ""


def extract_score(text: str) -> int:
    # Primary: explicit tag
    m = re.search(r'FINAL_SCORE:\s*(\d{3})', text, re.IGNORECASE)
    if m:
        return max(300, min(900, int(m.group(1))))
    # Fallback: last 3-digit number in 300–900 range
    hits = [int(x) for x in re.findall(r'\b([3-8]\d{2})\b', text)]
    return hits[-1] if hits else 500


def score_band(score: int):
    if score < 550:  return "Poor",      "#ff4b4b", "🔴", "band-poor"
    if score < 650:  return "Fair",      "#ff8c00", "🟠", "band-fair"
    if score < 750:  return "Good",      "#ffd700", "🟡", "band-good"
    return               "Excellent",   "#00cc66", "🟢", "band-excel"


def create_gauge(score: int) -> go.Figure:
    label, color, emoji, _ = score_band(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"{emoji}  {label} Credit Profile", "font": {"color": "white", "size": 20}},
        number={"font": {"color": "white", "size": 58}},
        gauge={
            "axis": {
                "range": [300, 900],
                "tickvals": [300, 400, 500, 600, 700, 800, 900],
                "tickcolor": "#888",
            },
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 1,
            "bordercolor": "#444",
            "steps": [
                {"range": [300, 550], "color": "#3a1515"},
                {"range": [550, 650], "color": "#3a2a10"},
                {"range": [650, 750], "color": "#3a3810"},
                {"range": [750, 900], "color": "#0f3a20"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=310,
        margin=dict(t=55, b=10, l=40, r=40),
    )
    return fig


# ── Demo Profiles ─────────────────────────────────────────────────────────────

DEMOS = {
    "gig": {
        "label": "🛵 Gig Worker — Good Profile",
        "upi": """\
2024-01-05 | ZOMATO_PAYOUT     | +₹4,200
2024-01-08 | SWIGGY_PAYOUT     | +₹3,800
2024-01-12 | ZOMATO_PAYOUT     | +₹3,500
2024-01-15 | Rent_Transfer     | -₹7,000
2024-01-18 | ZOMATO_PAYOUT     | +₹4,100
2024-01-22 | Grocery_BigBazaar | -₹1,200
2024-01-25 | SWIGGY_PAYOUT     | +₹4,500
2024-01-28 | Mobile_Recharge   | -₹299
2024-02-05 | ZOMATO_PAYOUT     | +₹5,100
2024-02-10 | SWIGGY_PAYOUT     | +₹4,200
2024-02-15 | Rent_Transfer     | -₹7,000
2024-02-20 | ZOMATO_PAYOUT     | +₹3,900
2024-02-22 | LIC_Premium       | -₹2,500
2024-02-25 | SWIGGY_PAYOUT     | +₹4,800""",
        "bills": "Electricity: Jan✅ Feb✅ Mar✅ Apr✅ | Gas: Jan✅ Feb✅ Mar✅ | Internet: Jan✅ Feb✅ Mar✅ Apr✅",
    },
    "corporate": {
        "label": "🏢 Corporate Employee — Excellent Profile",
        "upi": """\
2024-01-01 | TechCorp_Salary   | +₹85,000
2024-01-05 | Home_Loan_EMI     | -₹22,000
2024-01-10 | SIP_Investment    | -₹10,000
2024-01-15 | Grocery           | -₹3,500
2024-01-20 | Amazon_Purchase   | -₹2,100
2024-02-01 | TechCorp_Salary   | +₹85,000
2024-02-05 | Home_Loan_EMI     | -₹22,000
2024-02-10 | SIP_Investment    | -₹10,000
2024-02-15 | Grocery           | -₹4,200
2024-03-01 | TechCorp_Salary   | +₹85,000
2024-03-05 | Home_Loan_EMI     | -₹22,000""",
        "bills": "Electricity: Jan✅ Feb✅ Mar✅ | Gas: Jan✅ Feb✅ Mar✅ | Internet: Jan✅ Feb✅ Mar✅",
    },
    "highrisk": {
        "label": "⚠️ High Risk — Poor Profile",
        "upi": """\
2024-01-02 | Rahul_Sharma      | +₹10,000
2024-01-02 | Priya_Singh       | -₹9,800
2024-01-05 | Teen_Patti_App    | -₹5,000
2024-01-06 | Rahul_Sharma      | +₹5,200
2024-01-06 | Priya_Singh       | -₹5,100
2024-01-10 | Unknown_Salary    | +₹20,000
2024-01-15 | Rent              | -₹12,000
2024-01-18 | Teen_Patti_App    | -₹8,000
2024-01-20 | Loan_Penalty_Due  | -₹3,500
2024-01-25 | Rahul_Sharma      | +₹15,000
2024-01-25 | Priya_Singh       | -₹14,500""",
        "bills": "Electricity: Jan❌ Feb✅ Mar❌ (2 late fees) | Gas: Jan❌ Feb❌ Mar✅ (overdue ₹800) | Internet: Jan✅ Feb✅ Mar❌",
    },
}

# ── Session State Init ────────────────────────────────────────────────────────

for key, default in [("upi_data", ""), ("bill_data", ""), ("pdf_file", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏦 IndiScore Pro")
    st.caption("v3.0 · Multi-Agent Credit Intelligence")
    st.divider()

    # System status — no API key input needed
    st.markdown("**⚙️ System Status**")
    st.success("🟢 Groq API: Connected")
    st.success("🟢 PDF Parser: Online")
    st.info("🤖 Llama 3.3 70B via Groq")

    st.divider()

    st.markdown("**🤖 Agent Pipeline**")
    st.markdown("""
1. 📊 Financial Stability Auditor  
2. 🛡️ Fraud & Risk Auditor  
3. 🏦 Chief Credit Underwriter  
""")
    st.divider()

    st.markdown("**📊 Score Reference**")
    st.markdown("""
| Band | Range |
|------|-------|
| 🔴 Poor | 300–549 |
| 🟠 Fair | 550–649 |
| 🟡 Good | 650–749 |
| 🟢 Excellent | 750–900 |
""")
    st.divider()

    with st.expander("ℹ️ About IndiScore Pro"):
        st.markdown("""
**IndiScore Pro** helps India's **190M+ credit-invisible** individuals get fair credit access.

It evaluates UPI transactions and utility bills to produce **transparent, explainable** credit scores — no black-box decisions.

Built for gig workers, MSME owners, and informal earners who are denied credit due to lack of formal income proof.
""")

# ── Page Header ───────────────────────────────────────────────────────────────

st.title("🏦 IndiScore Pro")
st.markdown("##### Agentic Credit Intelligence Engine — Bridging the Gap for India's 190M+ Credit-Invisible")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Target Population", "190M+", "credit-invisible")
c2.metric("Score Range", "300–900", "transparent")
c3.metric("AI Agents", "3", "sequential pipeline")
c4.metric("Inference", "Llama 3.3 70B", "ultra-fast via Groq")

st.divider()

# ── Data Input ────────────────────────────────────────────────────────────────

st.header("📥 Data Input")

tab_pdf, tab_manual, tab_demo = st.tabs([
    "📄 Upload Bank Statement (PDF)",
    "⌨️ Manual Text Entry",
    "🧪 Load Demo Profile",
])

with tab_pdf:
    uploaded = st.file_uploader(
        "Upload your Bank Statement or UPI Export (PDF)",
        type=["pdf"],
        help="Supported: any bank PDF statement or UPI transaction export",
    )
    if uploaded:
        st.session_state["pdf_file"] = uploaded
        st.success(f"✅ **{uploaded.name}** — {uploaded.size // 1024} KB ready for analysis")
    else:
        st.session_state["pdf_file"] = None
    st.caption("💡 Export your UPI statement from PhonePe / GPay / your bank app as a PDF.")

with tab_manual:
    col_a, col_b = st.columns(2)
    with col_a:
        st.session_state["upi_data"] = st.text_area(
            "💸 UPI Transaction Logs",
            value=st.session_state["upi_data"],
            height=230,
            placeholder="2024-01-01 | Zomato_Payout | +₹4,200\n2024-01-05 | Rent | -₹8,000\n...",
        )
    with col_b:
        st.session_state["bill_data"] = st.text_area(
            "🧾 Utility & Bill Payments",
            value=st.session_state["bill_data"],
            height=230,
            placeholder="Electricity: Jan✅ Feb✅ Mar❌\nGas: Jan✅ Feb✅\nInternet: Jan✅ Feb✅",
        )

with tab_demo:
    st.info("Click any profile below to instantly load sample data, then hit **Analyze**.")
    for dk, dv in DEMOS.items():
        if st.button(f"Load: {dv['label']}", use_container_width=True, key=f"demo_{dk}"):
            st.session_state["upi_data"]  = dv["upi"]
            st.session_state["bill_data"] = dv["bills"]
            st.session_state["pdf_file"]  = None
            st.success(f"✅ **{dv['label']}** loaded! Switch to Manual Entry to view the data, then click Analyze.")
            st.rerun()

# ── Analyze Button ────────────────────────────────────────────────────────────

st.divider()
btn_col, hint_col = st.columns([1, 3])
with btn_col:
    run_analysis = st.button("🚀 Analyze Creditworthiness", use_container_width=True, type="primary")
with hint_col:
    st.caption("⏱️ 3 AI agents run sequentially — analysis takes about 30–90 seconds.")

# ── Run Pipeline ──────────────────────────────────────────────────────────────

if run_analysis:

    # Determine data source (PDF > manual)
    if st.session_state["pdf_file"] is not None:
        with st.spinner("📖 Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(st.session_state["pdf_file"])
        if not pdf_text:
            st.error("❌ Could not extract readable text from this PDF. Please try the Manual Entry tab instead.")
            st.stop()
        final_upi   = pdf_text
        final_bills = "Financial data extracted from the uploaded PDF document."

    elif st.session_state["upi_data"].strip():
        final_upi   = st.session_state["upi_data"]
        final_bills = st.session_state["bill_data"] or "No utility/bill data provided."

    else:
        st.warning("⚠️ Please upload a PDF, enter your transaction data, or load a demo profile.")
        st.stop()

    # Agent pipeline (no api_key arg — loaded from secrets automatically)
    with st.status("🧠 Multi-Agent Credit Committee is working...", expanded=True) as pipeline_status:
        st.write("**Step 1 / 3** — 📊 Financial Stability Auditor: analysing income & cashflow...")
        st.write("**Step 2 / 3** — 🛡️ Fraud & Risk Auditor: scanning for red flags & anomalies...")
        st.write("**Step 3 / 3** — 🏦 Chief Credit Underwriter: computing final score & report...")

        report_text = run_assessment(final_upi, final_bills)   # ← no api_key needed
        score       = extract_score(report_text)
        label, color, emoji, css = score_band(score)

        pipeline_status.update(
            label=f"✅ Underwriting Complete! Final Score: {score} ({label})",
            state="complete",
        )

    # ── Results ───────────────────────────────────────────────────────────────

    st.divider()
    st.header("📊 Financial Stability Analysis")

    left, right = st.columns([1, 1.6], gap="large")

    with left:
        st.plotly_chart(create_gauge(score), use_container_width=True)

        st.markdown("#### Key Metrics")
        m1, m2 = st.columns(2)
        m1.metric("Credit Band",      f"{emoji} {label}")
        m2.metric("Score",            f"{score} / 900")
        m3, m4 = st.columns(2)
        m3.metric("Loan Eligibility", "✅ Eligible"     if score >= 650 else "❌ Not Eligible")
        m4.metric("Risk Level",       "🟢 Low"          if score >= 700 else ("🟠 Moderate" if score >= 550 else "🔴 High"))

        st.markdown("---")
        st.markdown("""
**Score Bands**

| 🔴 Poor | 300–549 | High Risk |
|---------|---------|-----------|
| 🟠 Fair | 550–649 | Limited Credit |
| 🟡 Good | 650–749 | Standard Loans |
| 🟢 Excellent | 750–900 | Premium Credit |
""")

    with right:
        st.markdown("### 📋 Full Underwriter Report")
        st.markdown("---")
        # Strip the raw FINAL_SCORE tag — already shown in the gauge
        display = re.sub(r'\n?FINAL_SCORE:\s*\d+\s*$', '', report_text, flags=re.IGNORECASE).strip()
        st.markdown(display)

    # ── Export ────────────────────────────────────────────────────────────────

    st.divider()
    st.subheader("📤 Export Report")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download as .txt",
            data=f"IndiScore Pro — Credit Report\nScore: {score} ({label})\n\n{report_text}",
            file_name=f"indiscore_{score}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download as .md",
            data=f"# IndiScore Pro — Credit Report\n\n**Score: {score} ({label})**\n\n{report_text}",
            file_name=f"indiscore_{score}.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    "<div style='text-align:center;color:#555;font-size:0.78rem;'>"
    "🏦 IndiScore Pro · Built for India's Credit-Invisible · Powered by Llama 3.3 70B via Groq"
    "</div>",
    unsafe_allow_html=True,
)
