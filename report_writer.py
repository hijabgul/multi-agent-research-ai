from crewai import Agent

from llm_config import create_llm


def create_report_writer():

    llm = create_llm(temperature=0.3)

    return Agent(
        role="Research Report Writer",
        goal="Create a professional evidence-based research report.",
        backstory=(
            "You are an experienced research writer. "
            "You turn verified research into a clear, "
            "well-structured report."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
