%%writefile agents.py
import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

def run_assessment(upi_data, bill_data, api_key):
    # We ignore the api_key passed from the UI and use your Groq key directly
    # Or better yet: use the key from the UI if you decide to paste the Groq key there!
    
    groq_key = "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"
    
    # Initialize the Groq LLM (Llama 3 70B is excellent for reasoning)
    llm = ChatGroq(
        temperature=0.1,
        groq_api_key=groq_key,
        model_name="llama3-70b-8192"
    )

    # Agent 1: The Transaction Expert
    tx_agent = Agent(
        role='UPI Transaction Specialist',
        goal='Analyze financial stability from raw UPI logs.',
        backstory='Expert in Indian digital payment patterns. You identify salary and rent flags.',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Agent 2: The Reliability Expert
    util_agent = Agent(
        role='Utility & Behavioral Analyst',
        goal='Assess reliability based on bill history.',
        backstory='You look for punctuality in utility payments as a sign of character.',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Agent 3: The Manager
    manager = Agent(
        role='Chief Credit Underwriter',
        goal='Generate a final credit score (300-900) and reasoning trace.',
        backstory='You synthesize reports into a final, transparent decision.',
        llm=llm,
        verbose=True
    )

    t1 = Task(description=f"Analyze UPI: {upi_data}", expected_output="Stability summary.", agent=tx_agent)
    t2 = Task(description=f"Analyze Bills: {bill_data}", expected_output="Reliability report.", agent=util_agent)
    t3 = Task(description="Provide Final Score & Reasoning.", expected_output="Markdown report.", agent=manager, context=[t1, t2])

    crew = Crew(
        agents=[tx_agent, util_agent, manager], 
        tasks=[t1, t2, t3], 
        process=Process.sequential
    )
    
    return str(crew.kickoff())
