import os

# Fix CrewAI cache breakpoint issue with Groq/OpenAI-compatible providers
try:
    import crewai.llms.cache as crew_cache
    crew_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

from crewai import LLM


def create_llm(temperature=0.1):
    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=temperature,
        max_tokens=1000
    )
