import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

def run_assessment(upi_data, bill_data, api_key):
    # Enforce active credential routing
    active_key = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    if not active_key:
        return "Error: Groq API Key is missing. Please provide it in the sidebar or application secrets."

    # Using the direct LangChain integration layout bypasses litellm serialization issues entirely
    my_llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=active_key,
        temperature=0.2
    )

    # --- AGENT DEFINITIONS ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Extract clean income and spending metrics from unstructured strings.',
        backstory='Expert analytical system trained in Indian banking habits and UPI transaction summaries.',
        llm=my_llm,  # Directly binding the LangChain model instance
        verbose=True,
        allow_delegation=False
    )

    risk_agent = Agent(
        role='Fraud & Risk Auditor',
        goal='Identify red flags, circular transfers, and signs of extreme financial stress.',
        backstory='Skeptical compliance engine checking for synthetic trade volume or gambling markers.',
        llm=my_llm, 
        verbose=True,
        allow_delegation=False
    )

    underwriter = Agent(
        role='Chief Credit Underwriter',
        goal='Synthesize raw auditor summaries into a unified credit safety evaluation score.',
        backstory='Senior risk framework manager that aggregates stability metrics against anomalies.',
        llm=my_llm, 
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
