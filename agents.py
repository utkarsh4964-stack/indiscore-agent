import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

def run_assessment(upi_data, bill_data, api_key):
    # Determine the active API key to use
    active_key = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    if not active_key:
        return "Error: Groq API Key is missing. Please provide it in the sidebar or application secrets."

    # Direct LangChain setup handles authentication cleanly outside litellm
    langchain_model = ChatGroq(
        model_name="llama-3.3-70b-specdec",  # Stable high-performance production variant
        groq_api_key=active_key,
        temperature=0.2
    )

    # --- AGENT DEFINITIONS ---
    # Passing the LangChain model object inside a configuration dictionary 
    # satisfies Pydantic's strict type schemas perfectly in modern CrewAI versions.
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract clean income and spending metrics from unstructured text inputs.',
        backstory='Expert analytical system specializing in Indian banking habits, UPI logs, and transaction statements.',
        config={"llm": langchain_model},
        verbose=True,
        allow_delegation=False
    )

    risk_agent = Agent(
        role='Fraud & Risk Auditor',
        goal='Identify red flags, circular transaction flows, and signs of severe financial distress.',
        backstory='Skeptical compliance engine checking for synthetic volume, high-velocity recycling, or gambling patterns.',
        config={"llm": langchain_model},
        verbose=True,
        allow_delegation=False
    )

    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize raw auditor summaries into a unified credit safety evaluation profile scoring between 300 and 900.',
        backstory='Senior risk framework manager that aggregates financial stability indicators against risk markers.',
        config={"llm": langchain_model},
        verbose=True,
        allow_delegation=False
    )

    # --- TASK DEFINITIONS ---
    t1 = Task(
        description=f"Parse through these financial inputs thoroughly: \nUPI Log Streams: {upi_data}\nBill Profiles: {bill_data}",
        expected_output="A structured summary mapping out primary spending streams and cash inflows.",
        agent=tx_agent
    )

    t2 = Task(
        description="Scan through the user inputs to flag recurring anomalies like gaming/gambling records, circular money bouncing, or consistent payment failure penalties.",
        expected_output="A clean vulnerability breakdown detailing any uncovered high-risk patterns.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Compile the data into a single finalized credit score assessment document.
        The layout must output exactly matching this structure:
        1. Executive Summary
        2. Financial Health Score Analysis
        3. Risk Assessment Breakdown
        4. Improvement Roadmap
        5. FINAL_SCORE: [300-900] (You MUST append this exact phrase at the very end, e.g., FINAL_SCORE: 720)""",
        expected_output="A clean markdown report that finishes explicitly with the uppercase anchor 'FINAL_SCORE: XXX'.",
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
