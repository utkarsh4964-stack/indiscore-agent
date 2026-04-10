import os
from crewai import Agent, Task, Crew, Process

def run_assessment(upi_data, bill_data, api_key):
    # SET ENVIRONMENT VARIABLES (CrewAI looks here automatically)
    os.environ["GROQ_API_KEY"] = "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"
    
    # Define the model string in the format CrewAI prefers
    # Format: provider/model-name
    model_string = "groq/llama3-70b-8192"

    # Agent 1: The Transaction Expert
    tx_agent = Agent(
        role='UPI Transaction Specialist',
        goal='Analyze financial stability from raw UPI logs.',
        backstory='Expert in Indian digital payment patterns.',
        llm=model_string,  # <--- Passing as a string
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: The Reliability Expert
    util_agent = Agent(
        role='Utility Analyst',
        goal='Assess payment reliability via utility bills.',
        backstory='Focuses on punctuality as a sign of credit character.',
        llm=model_string, # <--- Passing as a string
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: The Manager
    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Generate a final score and reasoning trace.',
        backstory='Reconciles data into a final decision.',
        llm=model_string, # <--- Passing as a string
        verbose=True
    )

    t1 = Task(description=f"Analyze UPI: {upi_data}", expected_output="Stability score 1-10.", agent=tx_agent)
    t2 = Task(description=f"Analyze Bills: {bill_data}", expected_output="Reliability score 1-10.", agent=util_agent)
    t3 = Task(description="Final Score & Reasoning.", expected_output="Detailed Markdown report.", agent=manager, context=[t1, t2])

    crew = Crew(
        agents=[tx_agent, util_agent, manager], 
        tasks=[t1, t2, t3], 
        process=Process.sequential
    )
    
    return str(crew.kickoff())
