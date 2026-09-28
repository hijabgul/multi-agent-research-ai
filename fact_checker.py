```python
from crewai import Agent

from llm_config import create_llm
from web_tool import WebResearchTool


def create_fact_checker():

    return Agent(
        role="Fact Checker",

        goal=(
            "Verify important claims using independent "
            "web sources."
        ),

        backstory=(
            "You are a professional fact checker. "
            "You use the Web Research Tool to verify claims "
            "and identify whether information is supported."
        ),

        tools=[
            WebResearchTool()
        ],

        llm=create_llm(temperature=0.1),

        verbose=False,

        allow_delegation=False
    )
```
