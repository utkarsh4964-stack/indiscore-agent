import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, api_key=None):
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    
    # Model Strategy
    worker_llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.1)
    decision_llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.1)

    # 1. DATA EXTRACTOR (8B) - Focuses on hard numbers
    extractor = Agent(
        role='Data Integrity Specialist',
        goal='Extract raw numbers and verify transaction authenticity.',
        backstory='You are a forensic accountant. You identify circular trading and fake volume.',
        llm=worker_llm
    )

    # 2. RISK AUDITOR (8B) - Focuses on behavioral red flags
    auditor = Agent(
        role='Behavioral Risk Analyst',
        goal='Identify gambling, credit-hunger, and lifestyle instability.',
        backstory='You look for patterns that suggest high probability of default.',
        llm=worker_llm
    )

    # 3. CHIEF UNDERWRITER (70B) - The "Judge"
    underwriter = Agent(
        role='Chief Underwriter',
        goal='Provide a final score and a status: APPROVED, REVIEW, or UNAPPROVED.',
        backstory='You balance raw cash flow against behavioral risks. You are conservative.',
        llm=decision_llm
    )

    t1 = Task(
        description=f"Map all income and expenses from: {upi_data}. Identify any circular transfers.",
        expected_output="A structured financial sheet: Income, Expense, Surplus, and Verification Status.",
        agent=extractor
    )

    t2 = Task(
        description="Analyze the narration for gambling, late fees, or high-risk discretionary spending.",
        expected_output="A Risk Intensity Report (1-10) with specific evidence.",
        agent=auditor
    )

    t3 = Task(
        description="""Generate the Final Credit Dossier. 
        Calculate the FINAL_SCORE [300-900].
        Assign ANALYSIS_STATUS:
        - APPROVED: If Score > 720 and Risk < 3.
        - REVIEW: If Score 600-720 or evidence is vague.
        - UNAPPROVED: If Score < 600 or hard defaults found.
        """,
        expected_output="Markdown report ending with: FINAL_SCORE: XXX and STATUS: XXX",
        agent=underwriter,
        context=[t1, t2]
    )

    crew = Crew(
        agents=[extractor, auditor, underwriter],
        tasks=[t1, t2, t3],
        process=Process.sequential
    )
    
    return str(crew.kickoff())
