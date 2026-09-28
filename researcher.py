import os

from crewai import Agent, LLM

from web_tool import WebResearchTool


def create_researcher():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.2
    )

    researcher = Agent(

        role="Web Researcher",

        goal=(
            "Find current and relevant information from "
            "the web and collect useful evidence."
        ),

        backstory=(
            "You are a professional web researcher. "
            "You search the internet for useful sources, "
            "collect evidence and record source URLs."
        ),

        tools=[
            WebResearchTool()
        ],

        llm=llm,

        verbose=False,

        allow_delegation=False
    )

    return researcher
