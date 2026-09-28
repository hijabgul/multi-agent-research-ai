from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_researcher():
    return Agent(
        role="Web Researcher",

        goal=(
            "Search the web and collect only the most important "
            "current facts and source URLs needed for the research question."
        ),

        backstory=(
            "You are a concise professional web researcher. "
            "You search for reliable sources and return only essential "
            "evidence. Never write a long explanation."
        ),

        tools=[WebResearchTool()],

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False,

        max_iter=2,

        max_retry_limit=1
    )
