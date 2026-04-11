import os
from crewai import Agent, Task, Crew, Process, LLM

def run_assessment(upi_data, bill_data, api_key):
    # Use provided key or fallback to environment
    os.environ["GROQ_API_KEY"] = api_key if api_key else os.environ.get("GROQ_API_KEY")
    
    # 2026 Production Model
    my_llm = LLM(model="groq/llama-3.3-70b-versatile")

    tx_agent = Agent(
        role='UPI Transaction Specialist',
        goal='Analyze financial stability from raw UPI logs.',
        backstory='Expert in Indian digital payment patterns. You look for consistent income and rent markers.',
        llm=my_llm, 
        verbose=True,
        allow_delegation=False
    )

    util_agent = Agent(
        role='Utility Analyst',
        goal='Assess payment reliability via utility bills.',
        backstory='Focuses on punctuality as a sign of financial character.',
        llm=my_llm,
        verbose=True,
        allow_delegation=False
    )

    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Generate a final score (300-900) and reasoning trace.',
        backstory='Reconciles data into a final, human-readable report.',
        llm=my_llm,
        verbose=True
    )

    t1 = Task(description=f"Analyze UPI: {upi_data}", expected_output="Stability analysis.", agent=tx_agent)
    t2 = Task(description=f"Analyze Bills: {bill_data}", expected_output="Reliability report.", agent=util_agent)
    
    # CRITICAL: Added explicit formatting instruction for the score
    t3 = Task(
        description="Summarize the findings. You MUST include a final score between 300 and 900. Format it exactly as 'FINAL_SCORE: XXX' at the very end.", 
        expected_output="Markdown report ending with FINAL_SCORE: [number].", 
        agent=manager, 
        context=[t1, t2]
    )

    crew = Crew(
        agents=[tx_agent, util_agent, manager], 
        tasks=[t1, t2, t3], 
        process=Process.sequential
    )
    
    result = crew.kickoff()
    return str(result)
