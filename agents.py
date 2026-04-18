import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key=None):
    """
    Executes a multi-agent credit audit using Groq Llama 3 models.
    """
    # Set API Key in environment for the LLM manager
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    
    # Define the Model - Using Llama 3.3 70B for high-reasoning accuracy
    # 'groq/' prefix triggers the litellm bridge within CrewAI
    my_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=4096
    )

    # --- AGENT 1: THE DATA INTEGRITY SPECIALIST ---
    extractor = Agent(
        role='Forensic Financial Auditor',
        goal='Extract clean financial metrics and detect fraud or circular trading.',
        backstory="""You are an expert at spotting 'window dressing' in bank statements. 
        You look for round-tripping (sending and receiving the same amount to the same person) 
        and identify the true source of income vs. casual UPI transfers.""",
        llm=my_llm,
        allow_delegation=False,
        verbose=True
    )

    # --- AGENT 2: THE BEHAVIORAL RISK ANALYST ---
    auditor = Agent(
        role='Behavioral Credit Analyst',
        goal='Identify high-risk lifestyle markers and credit-hungry behavior.',
        backstory="""You analyze the 'narration' of transactions. You flag gambling, 
        excessive late fees, loan app repayments, and inconsistencies in spending 
        versus income levels. You focus on the 'character' of the borrower.""",
        llm=my_llm,
        allow_delegation=False,
        verbose=True
    )

    # --- AGENT 3: THE CHIEF UNDERWRITER ---
    underwriter = Agent(
        role='Chief Underwriting Officer',
        goal='Synthesize all findings into a final credit decision.',
        backstory="""You are the final decision-maker. You balance the raw surplus found 
        by the Auditor against the behavioral risks found by the Analyst. You are 
        conservative and prioritize capital preservation.""",
        llm=my_llm,
        allow_delegation=True,
        verbose=True
    )

    # --- TASKS ---
    t1 = Task(
        description=f"""
        Analyze the following data:
        UPI LOGS: {upi_data}
        UTILITY BILLS: {bill_data}
        
        1. Calculate Total Monthly Income (Verified vs Unverified).
        2. Calculate Fixed vs Discretionary Expenses.
        3. Identify any 'Circular Transfers' or 'Loan App' keywords.
        """,
        expected_output="A structured summary of Cash Flow, Surplus, and Data Authenticity.",
        agent=extractor
    )

    t2 = Task(
        description="""
        Evaluate the transaction narration for:
        - Gambling/Betting platforms.
        - Multiple small 'Urgent' loans.
        - Lack of essential utility payments (suggesting instability).
        - Subscription consistency.
        """,
        expected_output="A Risk Intensity Report with a list of specific red or green flags found.",
        agent=auditor
    )

    t3 = Task(
        description="""
        Review the findings from the Auditor and Analyst to generate the final dossier.
        
        CRITICAL RULES:
        - If 'Circular Trading' or 'Gambling' is high, STATUS must be UNAPPROVED.
        - If Income is verified but transparency is low, STATUS must be REVIEW.
        - Provide a FINAL_SCORE between 300 and 900.
        
        Format the end of your report exactly as:
        FINAL_SCORE: [Number]
        STATUS: [APPROVED/REVIEW/UNAPPROVED]
        """,
        expected_output="A detailed credit report concluding with FINAL_SCORE and STATUS.",
        agent=underwriter,
        context=[t1, t2]
    )

    # --- EXECUTION ---
    crew = Crew(
        agents=[extractor, auditor, underwriter],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True
    )

    return str(crew.kickoff())
