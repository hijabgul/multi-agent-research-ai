from crewai import Agent

from llm_config import create_llm


def create_planner():

    return Agent(
        role="Research Planner",

        goal=(
            "Create a short and focused research plan "
            "for the user's question."
        ),

        backstory=(
            "You are a research planning specialist. "
            "You identify the most important areas that "
            "must be investigated."
        ),

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False
    )
