import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key):
    os.environ["GROQ_API_KEY"] = api_key if api_key else os.environ.get("GROQ_API_KEY")
    my_llm = LLM(model="groq/llama-3.3-70b-versatile")

    # AGENT 1: The Cashflow Expert
    tx_agent = Agent(
        role='Transaction Integrity Specialist',
        goal='Identify income consistency and essential vs. discretionary spending.',
        backstory='Expert at spotting "Salary" markers in UPI logs and calculating debt-to-income ratios.',
        llm=my_llm, verbose=True
    )

    # AGENT 2: The Reliability Expert
    util_agent = Agent(
        role='Behavioral Punctuality Analyst',
        goal='Analyze utility bill history to determine "Character" and "Willingness to Pay".',
        backstory='Looks for 12-month streaks of on-time payments as a proxy for financial discipline.',
        llm=my_llm, verbose=True
    )

    # AGENT 3: THE SKEPTIC (New for Hackathons)
    risk_agent = Agent(
        role='Anti-Fraud & Risk Auditor',
        goal='Identify potential red flags, circular transactions, or signs of financial distress.',
        backstory='Your job is to find reasons NOT to lend. Look for high-frequency low-value transfers or gambling markers.',
        llm=my_llm, verbose=True
    )

    # AGENT 4: The Manager
    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize agent reports into a final credit score and actionable roadmap.',
        backstory='Final decision maker. Balances the optimism of the Cashflow agent with the caution of the Risk agent.',
        llm=my_llm, verbose=True
    )

    t1 = Task(description=f"Analyze UPI Stability: {upi_data}", expected_output="Cashflow Health Score (1-10)", agent=tx_agent)
    t2 = Task(description=f"Analyze Bill Punctuality: {bill_data}", expected_output="Reliability Score (1-10)", agent=util_agent)
    t3 = Task(description="Audit for Fraud or Risk markers in the provided data.", expected_output="Risk Flag Assessment.", agent=risk_agent)
    
    t4 = Task(
        description="""Generate a FINAL report. 
        1. Summarize reasoning from all agents.
        2. Provide a 'Score Breakdown' (Stability, Reliability, Risk).
        3. Provide 3 specific 'Improvement Steps'.
        4. End with EXACTLY: 'FINAL_SCORE: XXX'""",
        expected_output="Professional Underwriting Report with FINAL_SCORE tag.",
        agent=manager,
        context=[t1, t2, t3]
    )

    crew = Crew(agents=[tx_agent, util_agent, risk_agent, manager], tasks=[t1, t2, t3, t4], process=Process.sequential)
    return str(crew.kickoff())
