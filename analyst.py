import os

from crewai import Agent, LLM


def create_analyst():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.2
    )

    analyst = Agent(

        role="Source Analyst",

        goal=(
            "Analyze the collected research and identify "
            "important facts, evidence, patterns and disagreements."
        ),

        backstory=(
            "You are a research analyst. "
            "You carefully examine collected information, "
            "separate facts from opinions and organize evidence."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False
    )

    return analyst
