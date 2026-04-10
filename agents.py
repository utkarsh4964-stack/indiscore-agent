import os
from crewai import Agent, Task, Crew, Process

def run_assessment(upi_data, bill_data, api_key):
    # Instead of creating a complex LangChain object, 
    # we pass the model name as a string and the key.
    # CrewAI will handle the instantiation internally.
    
    os.environ["OPENAI_API_KEY"] = api_key
    model_name = "gpt-4o-mini"

    # Agent 1: The Transaction Expert
    tx_agent = Agent(
        role='UPI Transaction Specialist',
        goal='Analyze financial stability from raw UPI logs.',
        backstory='Expert in Indian digital payment patterns.',
        llm=model_name, # Just pass the string
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: The Reliability Expert
    util_agent = Agent(
        role='Utility Analyst',
        goal='Assess payment reliability via utility bills.',
        backstory='Focuses on punctuality as a sign of credit character.',
        llm=model_name,
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: The Manager
    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Generate a final score and reasoning trace.',
        backstory='Reconciles data into a final decision.',
        llm=model_name,
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
