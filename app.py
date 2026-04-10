import streamlit as st
from agents import run_assessment

st.set_page_config(page_title="IndiScore AI", page_icon="🇮🇳")
st.title("🇮🇳 IndiScore: Agentic Credit Scoring")
st.markdown("---")

# Security: Try to get API key from Streamlit Secrets first
api_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("Enter OpenAI API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    upi_input = st.text_area("Paste UPI History", height=200, placeholder="Salary +45000, Rent -15000...")
with col2:
    bill_input = st.text_area("Utility History", height=200, placeholder="Airtel: On-time, BESCOM: 2 days late...")

if st.button("🚀 Run Agentic Assessment"):
    if not api_key:
        st.error("Please provide an OpenAI API Key!")
    elif upi_input and bill_input:
        with st.status("Agents are analyzing data silos...", expanded=True) as status:
            result = run_assessment(upi_input, bill_input, api_key)
            status.update(label="Analysis Complete!", state="complete", expanded=False)
        st.markdown(result)
    else:
        st.warning("Please fill in both data fields.")
