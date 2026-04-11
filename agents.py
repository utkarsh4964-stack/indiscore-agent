import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key):
    # API Configuration
    os.environ["GROQ_API_KEY"] = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    # Using Llama 3.3 70B for high-reasoning tasks
    my_llm = LLM(model="groq/llama-3.3-70b-versatile")

    # --- AGENT 1: The Cashflow Specialist ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract net income, rent-to-income ratio, and discretionary spending patterns from raw transaction text.',
        backstory='Expert in Indian banking and UPI ecosystems. You are skilled at identifying salary markers, gig-payouts, and recurring investments in messy bank statements.',
        llm=my_llm, verbose=True
    )

    # --- AGENT 2: The Fraud Skeptic ---
    risk_agent = Agent(
        role='Fraud & Risk Auditor',
        goal='Identify red flags, circular transactions, and signs of financial distress.',
        backstory='You are a skeptical auditor. You look for synthetic volume inflation (money moving in circles) and risky spending patterns like gambling or multiple late-payment penalties.',
        llm=my_llm, verbose=True
    )

    # --- AGENT 3: The Manager ---
    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize agent reports into a final 300-900 score with an explainable reasoning trace.',
        backstory='You are the final decision-maker. You reconcile the data from the stability auditor and the risk auditor to provide a fair, transparent credit assessment.',
        llm=my_llm, verbose=True
    )

    # --- TASKS ---
    t1 = Task(
        description=f"Analyze the following financial data (could be raw text from a PDF or manual logs): \n{upi_data}\n{bill_data}\nIdentify recurring income, rent, and monthly stability.",
        expected_output="A structured summary of cashflow health and payment punctuality.",
        agent=tx_agent
    )

    t2 = Task(
        description="Audit the provided data for risk markers: gambling, circular transfers, or overdue bill penalties.",
        expected_output="A Risk Assessment report highlighting specific red flags or a 'Clear' status.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Generate the FINAL Underwriting Report:
        1. Executive Summary: The narrative of the user's financial character.
        2. Financial Health: Score out of
