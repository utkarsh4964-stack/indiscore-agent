import os
from crewai import Agent, LLM
from dotenv import load_dotenv

# Load environment variables (Make sure GROQ_API_KEY is in your .env or Streamlit Secrets)
load_dotenv()

# Define the LLM with the correct provider prefix
# The prefix "groq/" tells CrewAI to use the Groq bridge (requires litellm installed)
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY") 
)

class IndiScoreAgents:
    def credit_analyst_agent(self):
        return Agent(
            role="Senior Credit Risk Analyst",
            goal="Analyze alternative data points to assess creditworthiness for NTC (New-to-Credit) users.",
            backstory=(
                "You are an expert in Indian financial systems and alternative credit scoring. "
                "Your strength lies in identifying patterns in non-traditional data like utility bills, "
                "digital footprints, and behavioral trends to predict repayment capability."
            ),
            allow_delegation=False,
            verbose=True,
            llm=groq_llm
        )

    def data_validator_agent(self):
        return Agent(
            role="Financial Data Integrity Specialist",
            goal="Cross-verify and clean raw user data to ensure accuracy before credit scoring.",
            backstory=(
                "You specialize in detecting anomalies and fraudulent entries in financial datasets. "
                "You ensure that the multi-agent system operates on high-fidelity data."
            ),
            allow_delegation=False,
            verbose=True,
            llm=groq_llm
        )

    def strategy_agent(self):
        return Agent(
            role="Fintech Product Strategist",
            goal="Synthesize technical credit scores into actionable business insights and loan limit recommendations.",
            backstory=(
                "You bridge the gap between technical risk data and business growth. "
                "You provide the final 'IndiScore' report that banks and NBFCs use to make lending decisions."
            ),
            allow_delegation=True,
            verbose=True,
            llm=groq_llm
        )
