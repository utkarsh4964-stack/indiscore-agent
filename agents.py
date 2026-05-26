"""
agents.py — IndiScore Pro Multi-Agent Credit Pipeline
Implements a 3-agent sequential pipeline using the Groq SDK directly,
replacing the unstable CrewAI dependency that caused Streamlit Cloud failures.
"""

import os
from groq import Groq


def _call_llm(client: Groq, system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    """Single LLM call wrapper with error handling."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Agent Error: {e}]"


def run_assessment(upi_data: str, bill_data: str, api_key: str) -> str:
    """
    Runs a sequential 3-agent credit assessment pipeline.

    Agent 1 — Financial Stability Auditor: cashflow & income analysis
    Agent 2 — Fraud & Risk Auditor: anomaly & red-flag detection
    Agent 3 — Chief Credit Underwriter: final score + explainable report

    Returns a Markdown report ending with: FINAL_SCORE: XXX
    """
    key = api_key.strip() if api_key else os.environ.get("GROQ_API_KEY", "")
    if not key:
        return (
            "**⛔ Configuration Error:** No Groq API key provided.\n\n"
            "Please enter your Groq API key in the sidebar to run the analysis."
        )

    client = Groq(api_key=key)

    # ── AGENT 1: Financial Stability Auditor ──────────────────────────────────
    tx_report = _call_llm(
        client=client,
        system_prompt="""You are a Financial Stability Auditor specialising in Indian banking, UPI, and gig-economy ecosystems.
Your task is to analyse raw UPI transaction logs and bank statements to:
- Identify all income sources and measure consistency month-over-month
- Detect EMI, rent, and recurring payment patterns
- Assess savings rate and debt-to-income ratio
- Recognise gig-platform payouts (Zomato, Swiggy, Ola, Urban Company, etc.)
- Produce a structured cashflow health summary

Be concise, objective, and structured.""",
        user_message=f"""Analyse the financial data below and produce a structured cashflow summary.

=== UPI TRANSACTION DATA ===
{upi_data}

=== UTILITY / BILL DATA ===
{bill_data}

Output format:
**Income Consistency Score:** X/10
**Spending Discipline Score:** X/10
**Estimated Monthly Income:** ₹XX,XXX
**Debt-to-Income Ratio:** XX%
**Key Findings:**
- finding 1
- finding 2
- finding 3""",
        max_tokens=800,
    )

    # ── AGENT 2: Fraud & Risk Auditor ─────────────────────────────────────────
    risk_report = _call_llm(
        client=client,
        system_prompt="""You are a sceptical Fraud & Risk Auditor for an Indian fintech lending company.
Your task is to detect:
- Circular / round-trip transactions (money immediately returned)
- Synthetic volume inflation (artificial transactions to inflate income)
- Gambling or high-risk spending (Teen Patti, fantasy sports, crypto)
- Overdue payment penalties and late fees
- Sudden unexplained large inflows or outflows
- Any signs of financial distress or misrepresentation

Rate each risk factor clearly and assign an overall risk score.""",
        user_message=f"""Audit the following data for fraud markers and risk signals.

=== UPI TRANSACTION DATA ===
{upi_data}

=== UTILITY / BILL DATA ===
{bill_data}

=== CASHFLOW ANALYSIS (from Agent 1) ===
{tx_report}

Output format:
**Overall Fraud Risk:** Low / Medium / High
**Risk Score:** X/10 (10 = highest risk)
**Red Flags Detected:**
- flag 1 (or "None detected")
**Positive Signals:**
- signal 1""",
        max_tokens=800,
    )

    # ── AGENT 3: Chief Credit Underwriter ─────────────────────────────────────
    final_report = _call_llm(
        client=client,
        system_prompt="""You are the Chief Credit Underwriter at IndiScore Pro, an Indian fintech company.
You synthesise financial stability analysis and risk reports to produce a final credit score between 300 and 900.

Scoring bands:
- 300–549: Poor — high risk, not eligible for most credit
- 550–649: Fair — limited credit access, higher interest rates
- 650–749: Good — eligible for standard personal loans
- 750–900: Excellent — eligible for premium credit products

Your report must be professional, transparent, and follow the exact output format.
You MUST end your report with the exact line: FINAL_SCORE: [number] where [number] is between 300 and 900.""",
        user_message=f"""Generate the final credit underwriting report based on the two agent analyses below.

=== FINANCIAL STABILITY ANALYSIS (Agent 1) ===
{tx_report}

=== FRAUD & RISK ASSESSMENT (Agent 2) ===
{risk_report}

Write a professional Markdown report with these exact sections:

## 📊 Executive Summary
(2–3 sentence overview of the applicant's financial profile)

## 💰 Financial Health Assessment
(Key income, spending, and savings insights)

## 🚨 Risk & Fraud Assessment
(Risk level, red flags, and positive signals)

## 🗺️ Improvement Roadmap
(3–5 actionable steps to improve the credit score)

## 📌 Underwriter Decision
(Final lending recommendation with rationale)

FINAL_SCORE: [300–900]""",
        max_tokens=1800,
    )

    return final_report
