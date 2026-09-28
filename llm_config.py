import os

# ============================================================
# CREWAI GROQ CACHE BREAKPOINT FIX
# ============================================================

try:
    import crewai.llms.cache as crew_cache

    crew_cache.mark_cache_breakpoint = lambda msg: msg

except Exception:
    pass


# IMPORTANT:
# Import LLM AFTER the cache breakpoint patch
from crewai import LLM


def create_llm(temperature=0.2):

    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=temperature
    )
