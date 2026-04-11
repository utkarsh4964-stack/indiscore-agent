import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key=None):
    # Use Streamlit secret if no manual key is provided
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY")
    
    # Improvement: Optimized LLM Config for Fintech logic
    fast_llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.1)

    # --- AGENT IMPROVEMENTS ---
    tx_agent = Agent(
        role='Financial Stability Auditor',
        goal='Identify net income and stability from localized Indian transaction logs.',
        backstory="""You are an expert in Indian UPI and banking narration. You recognize 
        'Dudh', 'Kirana', 'Zomato Payout', and 'Rent' as valid financial markers. You 
        calculate a net monthly surplus after essential expenses.""",
        llm=fast_llm
    )

    risk_agent = Agent(
        role='Risk & Fraud Skeptic',
        goal='Detect circular trading, gambling, and credit hunger patterns.',
        backstory="""You protect the lender. You look for money moving in circles between 
        friends to fake volume, payments to betting apps, and signs of 'Credit Hunger' 
        like multiple late fees or small loan inquiries.""",
        llm=fast_llm
    )

    # Improvement: New Agent for User Guidance
    coach_agent = Agent(
        role='Financial Health Coach',
        goal='Create a 30-day action plan to improve the user score.',
        backstory="""You are helpful and encouraging. You look at the weaknesses found by 
        other agents and provide 3 specific steps to boost creditworthiness.""",
        llm=fast_llm
    )

    # --- UPDATED TASKS ---
    t1 = Task(
        description=f"Analyze the raw transaction text: {upi_data[:8000]}", # Context capping
        expected_output="A structured summary of income vs essential expenses.",
        agent=tx_agent
    )

    t2 = Task(
        description="Search for gambling markers, circular patterns, or payment defaults.",
        expected_output="A risk flag report with specific transaction examples.",
        agent=risk_agent
    )

    t3 = Task(
        description="""Synthesize the final report. 
        Format: 
        1. Executive Summary 
        2. Financial Health Score (1-10) 
        3. Risk Assessment (1-10)
        4. ACTION PLAN: 3 steps to increase score.
        5. FINAL_SCORE: [300-900]""",
        expected_output="Markdown report ending with FINAL_SCORE: XXX",
        agent=coach_agent, # Coach now handles the final synthesis for a better user tone
        context=[t1, t2]
    )

    crew = Crew(
        agents=[tx_agent, risk_agent, coach_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential
    )
    
    return str(crew.kickoff())
