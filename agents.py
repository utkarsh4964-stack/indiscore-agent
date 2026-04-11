import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key=None):
    # Ensure API Key is set
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY")
    
    # STRATEGY: Use 8B for extraction (High Rate Limit) and 70B for reasoning (Lower Rate Limit)
    worker_llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.1)
    decision_llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.1)

    # --- AGENT DEFINITIONS ---
    tx_agent = Agent(
        role='Financial Data Extractor',
        goal='Accurately extract income and spending from raw bank text.',
        backstory='You are a high-speed data processor focused on identifying transaction types.',
        llm=worker_llm, # Using 8B here
        verbose=True
    )

    risk_agent = Agent(
        role='Risk Specialist',
        goal='Identify red flags like gambling or circular transfers.',
        backstory='You look for high-risk behavioral patterns in financial data.',
        llm=worker_llm, # Using 8B here
        verbose=True
    )

    underwriter = Agent(
        role='Chief Underwriter',
        goal='Provide the final 300-900 score and executive summary.',
        backstory='You are the senior decision maker. You provide complex reasoning and guidance.',
        llm=decision_llm, # Using 70B for the "Brain"
        verbose=True
    )

    # --- TASK DEFINITIONS ---
    t1 = Task(
        description=f"Analyze transaction logs: {upi_data[:6000]}", # Capping text to save tokens
        expected_output="A structured summary of income and expenses.",
        agent=tx_agent
    )

    t2 = Task(
        description="Check for gambling, late fees, or suspicious transfers in the data.",
        expected_output="A bulleted list of risk findings.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Synthesize the final credit report.
        1. Executive Summary
        2. Financial Health Score (1-10)
        3. Risk Assessment (1-10)
        4. ACTION PLAN: 3 steps to boost score.
        5. FINAL_SCORE: [300-900]""",
        expected_output="Comprehensive Markdown report ending with FINAL_SCORE: XXX.",
        agent=underwriter,
        context=[t1, t2]
    )

    crew = Crew(
        agents=[tx_agent, risk_agent, underwriter],
        tasks=[t1, t2, t3],
        process=Process.sequential
    )
    
    return str(crew.kickoff())
