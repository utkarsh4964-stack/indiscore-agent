import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

def run_assessment(upi_data, bill_data, api_key):
    # Determine the API key to use
    active_key = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    if not active_key:
        return "Error: Groq API Key is missing. Please provide it in the sidebar or application secrets."

    # Direct LangChain instantiation completely bypasses crewai/llm.py and litellm errors
    my_llm = ChatGroq(
        model_name="llama-3.3-70b-specdec", # High-throughput stable Groq production model ID
        groq_api_key=active_key,
        temperature=0.2
    )

    # --- AGENT DEFINITIONS ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract income and spending patterns from raw text.',
        backstory='Expert in Indian banking ecosystems, transaction logs, and UPI statements.',
        llm=my_llm, 
        verbose=True,
        allow_delegation=False
    )

    risk_agent = Agent(
        role='Fraud & Risk Auditor',
        goal='Identify red flags, circular transactions, and signs of financial distress.',
        backstory='Skeptical auditor looking for synthetic volume, heavy credit recycling, or gambling patterns.',
        llm=my_llm, 
        verbose=True,
        allow_delegation=False
    )

    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize reports into a final creditworthiness assessment scoring between 300 and 900.',
        backstory='Final decision-maker who balances stability metrics against risk indices.',
        llm=my_llm, 
        verbose=True,
        allow_delegation=False
    )

    # --- TASK DEFINITIONS ---
    t1 = Task(
        description=f"Analyze the following financial data carefully: \nUPI/Bank Logs: {upi_data}\nBills: {bill_data}",
        expected_output="A structured summary mapping average monthly cash flows, regular income spikes, and operational expenses.",
        agent=tx_agent
    )

    t2 = Task(
        description="Audit the provided transactional data specifically for risk markers: gaming/gambling transactions, repetitive circular transfers, or late-payment penalties.",
        expected_output="A comprehensive Risk Assessment report highlighting critical vulnerabilities or anomalies.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Generate the FINAL Underwriting Report by combining the findings.
        The report must be meticulously formatted and structured as follows:
        1. Executive Summary
        2. Financial Health Score Analysis
        3. Risk Assessment Breakdown
        4. Improvement Roadmap
        5. FINAL_SCORE: [300-900] (You MUST append this exact phrase at the very end, e.g., FINAL_SCORE: 720)""",
        expected_output="A professional Markdown report concluding with the absolute string 'FINAL_SCORE: XXX'.",
        agent=underwriter,
        context=[t1, t2]
    )

    # --- EXECUTION ---
    crew = Crew(
        agents=[tx_agent, risk_agent, underwriter],
        tasks=[t1, t2, t3],
        process=Process.sequential
    )
    
    return str(crew.kickoff())
