from crewai import Agent

from llm_config import create_llm


def create_researcher():
    return Agent(
        role="Web Researcher",
        goal=(
            "Analyze the provided web search results and extract "
            "the most relevant facts and sources for the research question."
        ),
        backstory=(
            "You are a professional web researcher. "
            "You carefully examine search results, identify useful evidence, "
            "and produce concise research findings with source URLs. "
            "Do not invent information."
        ),
        llm=create_llm(temperature=0.1),
        verbose=False,
        allow_delegation=False,
        max_iter=1,
        max_retry_limit=1
    )
