from crewai import Agent

from llm_config import create_llm


def create_report_writer():

    return Agent(
        role="Research Report Writer",

        goal=(
            "Write a clear and concise evidence-based "
            "research report."
        ),

        backstory=(
            "You are a professional research writer. "
            "You transform verified evidence into a "
            "well-structured report without inventing facts."
        ),

        llm=create_llm(temperature=0.2),

        verbose=False,

        allow_delegation=False
    )
