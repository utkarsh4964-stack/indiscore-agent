import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key):
    # API Configuration
    os.environ["GROQ_API_KEY"] = api_key if api_key else os.environ.get("GROQ_API_KEY")
    my_llm = LLM(model="groq/llama-3.3-70b-versatile")

    # --- AGENT DEFINITIONS ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract net income, rent-to-income ratio, and discretionary spending patterns.',
        backstory='Expert in Indian UPI ecosystems. You identify salary, gig-payouts (Zomato/Swiggy), and recurring investments.',
        llm=my_llm, verbose=True
    )

    risk_agent = Agent(
        role='Fraud & Risk Skeptic',
        goal='Identify red flags, circular transactions, and gambling markers.',
        backstory='Your job is to protect the lender. Look for synthetic volume inflation and signs of financial distress.',
        llm=my_llm, verbose=True
    )

    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize agent reports into a final 300-900 score with a reasoning trace.',
        backstory='You reconcile the optimism of the Stability agent with the caution of the Risk agent.',
        llm=my_llm, verbose=True
    )

    # --- TASK DEFINITIONS ---
    t1 = Task(
        description=f"Analyze UPI Logs: {upi_data}\nAnalyze Bills: {bill_data}",
        expected_output="A detailed summary of monthly net cashflow and payment punctuality.",
        agent=tx_agent
    )

    t2 = Task(
        description="Audit the provided data for risk markers like gambling, late fees, or circular transfers.",
        expected_output="A Risk Flag report highlighting specific anomalies or 'Clear' status.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Generate the Final Underwriting Report.
        1. Executive Summary: Why this score?
        2. Financial Health: Score out of 10.
        3. Risk Assessment: Score out of 10.
        4. Improvement Roadmap: 3 steps to boost score.
        5. FINAL_SCORE: [300-900] (MUST include this tag).""",
        expected_output="Professional Markdown Report ending with FINAL_SCORE: XXX.",
        agent=underwriter,
        context=[t1, t2]
    )

    crew = Crew(
        agents=[tx_agent, risk_agent, underwriter],
        tasks=[t1, t2, t3],
        process=Process.sequential
    )
    
    return str(crew.kickoff())
