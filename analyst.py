from crewai import Agent

from llm_config import create_llm


def create_analyst():

    return Agent(
        role="Source Analyst",

        goal=(
            "Analyze research findings and identify "
            "the strongest evidence."
        ),

        backstory=(
            "You examine research findings, separate "
            "strong evidence from weak claims and "
            "identify information requiring verification."
        ),

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False
    )
