from crewai import Agent

from llm_config import create_llm


def create_planner():

    llm = create_llm(temperature=0.2)

    return Agent(
        role="Research Planner",
        goal="Create a clear research plan for the user's question.",
        backstory=(
            "You are an experienced research planner. "
            "You divide complex questions into focused research areas "
            "and identify what evidence should be collected."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
