import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

def run_assessment(upi_data, bill_data, api_key):
    # Initialize the LLM (GPT-4o-mini is best for high impact at low cost)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, openai_api_key=api_key)

    # Agent 1: The Transaction Expert
    tx_agent = Agent(
        role='UPI Transaction Specialist',
        goal='Analyze financial stability from raw UPI logs.',
        backstory='Expert in Indian digital payment patterns. You look for recurring salary and rent.',
        llm=llm, verbose=True
    )

    # Agent 2: The Reliability Expert
    util_agent = Agent(
        role='Utility & Behavioral Analyst',
        goal='Assess payment reliability via utility bills.',
        backstory='You believe punctuality in electricity and phone bills reflects credit character.',
        llm=llm, verbose=True
    )

    # Agent 3: The Manager (Meta-Agent)
    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Generate a final score and reasoning trace.',
        backstory='You reconcile data from specialists into a final, explainable decision.',
        llm=llm, verbose=True
    )

    t1 = Task(description=f"Analyze UPI: {upi_data}", expected_output="Stability score 1-10.", agent=tx_agent)
    t2 = Task(description=f"Analyze Bills: {bill_data}", expected_output="Reliability score 1-10.", agent=util_agent)
    t3 = Task(description="Provide Final Score (300-900) & Reasoning Trace.", 
              expected_output="Detailed Markdown report.", 
              agent=manager, context=[t1, t2])

    crew = Crew(agents=[tx_agent, util_agent, manager], tasks=[t1, t2, t3], process=Process.sequential)
    return crew.kickoff()
