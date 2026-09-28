import os

from crewai import Agent, LLM


def create_report_writer():

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.3
    )

    writer = Agent(

        role="Research Report Writer",

        goal=(
            "Create a professional research report "
            "using the research, analysis and fact checking."
        ),

        backstory=(
            "You are an experienced research writer. "
            "You create clear, structured and evidence-based reports."
        ),

        llm=llm,

        verbose=False,

        allow_delegation=False
    )

    return writer
