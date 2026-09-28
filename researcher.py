from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_researcher():
    return Agent(
        role="Web Researcher",
        goal="Find reliable and current information from the internet.",
        backstory=(
            "You are a professional web researcher. "
            "You search the internet using the Web Research Tool "
            "and collect concise evidence with source URLs."
        ),
        tools=[WebResearchTool()],
        llm=create_llm(temperature=0.1),
        verbose=False,
        allow_delegation=False
    )
