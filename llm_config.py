import os

from crewai import LLM


def create_llm(temperature=0.2):

    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=temperature
    )
