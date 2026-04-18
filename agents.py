import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key=None):
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    
    # Force temperature to 0 for objective scoring
    my_llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    # 1. Forensic Agent
    extractor = Agent(
        role='Fraud Detection Specialist',
        goal='Identify fake transaction volume and circular trading.',
        backstory='You are a skeptical auditor. You assume users try to game the system.',
        llm=my_llm
    )

    # 2. Risk Agent
    auditor = Agent(
        role='Risk Analyst',
        goal='Flag gambling, defaults, and late fees.',
        backstory='You look for behavioral red flags that lead to loan default.',
        llm=my_llm
    )

    # 3. Final Judge
    underwriter = Agent(
        role='Chief Underwriter',
        goal='Assign a score and status based on strict penalty rules.',
        backstory='You are conservative. You would rather reject a good user than approve a bad one.',
        llm=my_llm
    )

    t1 = Task(
        description=f"Analyze: {upi_data}. Flag back-and-forth transfers between same parties as 'Circular Trading'.",
        expected_output="Verification report on data integrity.",
        agent=extractor
    )

    t2 = Task(
        description=f"Analyze: {bill_data}. Identify late payments or failed EMIs.",
        expected_output="Risk intensity summary.",
        agent=auditor
    )

    t3 = Task(
        description="""
        Synthesize findings into a final report.
        MANDATORY PENALTY RULES:
        - IF 'REVERSED' or 'Insufficient Funds' found: Set Score < 400 immediately.
        - IF 'Circular Trading' found: Set Score < 500 and STATUS: UNAPPROVED.
        - IF 'Gambling/Betting' found: Set STATUS: UNAPPROVED.
        
        Format the END of your response exactly as:
        FINAL_SCORE: [number]
        STATUS: [APPROVED/REVIEW/UNAPPROVED]
        """,
        expected_output="Final Dossier with Score and Status.",
        agent=underwriter,
        context=[t1, t2]
    )

    crew = Crew(agents=[extractor, auditor, underwriter], tasks=[t1, t2, t3])
    return str(crew.kickoff())
