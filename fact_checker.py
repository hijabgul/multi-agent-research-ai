import os

from crewai import Agent, LLM

from web_tool import WebResearchTool


def create_fact_checker():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.1
    )

    fact_checker = Agent(

        role="Fact Checker",

        goal=(
            "Verify important research claims using "
            "independent web sources."
        ),

        backstory=(
            "You are a careful fact checker. "
            "You compare claims with external sources "
            "and identify unsupported or conflicting information."
        ),

        tools=[
            WebResearchTool()
        ],

        llm=llm,

        verbose=False,

        allow_delegation=False
    )

    return fact_checker
