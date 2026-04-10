import streamlit as st

# --- STEP 1: CRITICAL SQLITE COMPATIBILITY PATCH ---
# This must happen BEFORE any other imports to prevent the "Oh No" crash
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass
# --------------------------------------------------

from agents import run_assessment

# Page Configuration
st.set_page_config(
    page_title="IndiScore: Agentic Credit AI",
    page_icon="💳",
    layout="centered"
)

# Custom Styling for the "Buzzword" Appeal
st.title("🇮🇳 IndiScore: Agentic Credit Assessment")
st.markdown("""
    **Transforming Financial Inclusion** for 190M credit-invisible Indians. 
    *Powered by Multi-Agent Orchestration & Explainable AI.*
""")
st.divider()

# --- STEP 2: SECRET & API KEY HANDLING ---
# If deployed on Streamlit Cloud, it looks for the secret. 
# If not found (like in local testing), it shows a sidebar input.
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.sidebar.warning("API Key not found in Secrets.")
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
else:
    st.sidebar.success("Connected via Streamlit Secrets ✅")

# --- STEP 3: USER INPUT SECTION ---
st.subheader("User Financial Profiles")
col1, col2 = st.columns(2)

with col1:
    upi_data = st.text_area(
        "UPI & Transaction Logs", 
        height=200,
        placeholder="e.g.\nSalary: +45,000\nRent: -12,000\nZomato: -450\nEMI: -3,500"
    )

with col2:
    bill_data = st.text_area(
        "Utility & Behavioral Data", 
        height=200,
        placeholder="e.g.\nAirtel Fiber: Paid on time\nElectricity: 5 days late (March)\nGas: Paid on time"
    )

# --- STEP 4: AGENT EXECUTION ---
if st.button("🚀 Run Multi-Agent Scoring"):
    if not api_key:
        st.error("Please provide an OpenAI API Key to start the agents.")
    elif upi_data and bill_data:
        # The Status container shows the "Agentic Thinking" process to the user
        with st.status("Initializing Specialist Agents...", expanded=True) as status:
            st.write("🕵️ Transaction Agent: Scanning UPI patterns for stability...")
            st.write("📡 Utility Agent: Analyzing bill punctuality...")
            st.write("⚖️ Manager Agent: Synthesizing results and reconciling conflicts...")
            
            # Call the logic from agents.py
            try:
                final_report = run_assessment(upi_data, bill_data, api_key)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
                
                st.subheader("📊 Final Assessment Report")
                st.info(final_report)
                
                st.success("Decision Explainability Trace generated successfully.")
            except Exception as e:
                st.error(f"An error occurred during agent orchestration: {e}")
                status.update(label="Analysis Failed", state="error")
    else:
        st.warning("Please enter data for both Transaction and Utility logs.")

# Footer
st.divider()
st.caption("IndiScore v1.0 | Built by Utkarsh Sharma | 2026 Hackathon Edition")
