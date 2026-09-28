from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_researcher():

    llm = create_llm(temperature=0.2)

    return Agent(
        role="Web Researcher",
        goal="Find current and reliable information from the web.",
        backstory=(
            "You are a professional web researcher. "
            "You search the web, collect evidence and keep track "
            "of the sources used."
        ),
        tools=[WebResearchTool()],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
