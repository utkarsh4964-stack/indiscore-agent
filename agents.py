ag:import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key):
    # API Configuration
    os.environ["GROQ_API_KEY"] = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    # Using Llama 3.3 70B
    my_llm = LLM(model="groq/llama-3.3-70b-versatile")

    # --- AGENT DEFINITIONS ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract income and spending patterns from raw text.',
        backstory='Expert in Indian banking ecosystems and UPI logs.',
        llm=my_llm, 
        verbose=True
    )

    risk_agent = Agent(
        role='Fraud & Risk Auditor',
        goal='Identify red flags, circular transactions, and signs of financial distress.',
        backstory='Skeptical auditor looking for synthetic volume or gambling patterns.',
        llm=my_llm, 
        verbose=True
    )

    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize reports into a final 300-900 score.',
        backstory='Final decision-maker who reconciles stability and risk data.',
        llm=my_llm, 
        verbose=True
    )

    # --- TASK DEFINITIONS ---
    t1 = Task(
        description=f"Analyze the following data: \nUPI: {upi_data}\nBills: {bill_data}",
        expected_output="A structured summary of cashflow health.",
        agent=tx_agent
    )

    t2 = Task(
        description="Audit the provided data for risk markers: gambling, circular transfers, or overdue bill penalties.",
        expected_output="A Risk Assessment report.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Generate the FINAL Underwriting Report:
        1. Executive Summary
        2. Financial Health Score
        3. Risk Assessment Score
        4. Improvement Roadmap
        5. FINAL_SCORE: [300-900] (MUST include this tag).""",
        expected_output="Professional Markdown Report ending with FINAL_SCORE: XXX.",
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
