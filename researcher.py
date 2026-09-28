from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_researcher():

    return Agent(
        role="Web Researcher",

        goal=(
            "Find current and reliable information "
            "from the web."
        ),

        backstory=(
            "You are a web research specialist. "
            "You search for relevant evidence and "
            "record useful source URLs."
        ),

        tools=[
            WebResearchTool()
        ],

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False
    )
