from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_researcher():
    return Agent(
        role="Web Researcher",
        goal="Find a few reliable facts and sources for the research question.",
        backstory=(
            "You are a concise web researcher. "
            "Use the web search tool and return short factual findings "
            "with source URLs."
        ),
        tools=[WebResearchTool()],
        llm=create_llm(temperature=0.1),
        verbose=False,
        allow_delegation=False,
        max_iter=2,
        max_retry_limit=1
    )
