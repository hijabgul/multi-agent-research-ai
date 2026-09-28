from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_fact_checker():

    return Agent(
        role="Fact Checker",

        goal=(
            "Verify important research claims using "
            "independent web sources."
        ),

        backstory=(
            "You are a fact-checking specialist. "
            "You compare claims with reliable sources "
            "and identify information that cannot be verified."
        ),

        tools=[
            WebResearchTool()
        ],

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False
    )
