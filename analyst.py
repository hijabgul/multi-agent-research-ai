from crewai import Agent

from llm_config import create_llm


def create_analyst():

    llm = create_llm(temperature=0.2)

    return Agent(
        role="Source Analyst",
        goal="Analyze research and identify important evidence and findings.",
        backstory=(
            "You carefully examine research sources, "
            "separate facts from opinions and organize evidence."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
