from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_fact_checker():

    llm = create_llm(temperature=0.1)

    return Agent(
        role="Fact Checker",
        goal="Verify important research claims using independent sources.",
        backstory=(
            "You carefully verify claims, compare sources "
            "and identify information that cannot be confirmed."
        ),
        tools=[WebResearchTool()],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
