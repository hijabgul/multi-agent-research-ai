import os

from crewai import Agent, LLM


def create_planner():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.2
    )

    planner = Agent(

        role="Research Planner",

        goal=(
            "Create a focused and practical research plan "
            "for the user's research question."
        ),

        backstory=(
            "You are an experienced research planner. "
            "You break a research question into important "
            "subtopics and identify what evidence is needed."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False
    )

    return planner
