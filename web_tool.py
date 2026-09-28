from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from ddgs import DDGS


class WebResearchInput(BaseModel):
    query: str = Field(
        ...,
        description="The exact web search query."
    )


class WebResearchTool(BaseTool):
    name: str = "web_research_tool"

    description: str = (
        "Search the internet for current information and facts. "
        "Use one parameter named query."
    )

    args_schema: Type[BaseModel] = WebResearchInput

    def _run(self, query: str) -> str:

        if not query or not query.strip():
            return "No search query was provided."

        try:
            results = DDGS().text(
                query.strip(),
                max_results=3
            )

        except Exception as e:
            return f"Web search failed: {str(e)}"

        if not results:
            return "No web results found."

        output = []

        for number, result in enumerate(results, start=1):

            title = result.get("title", "Untitled")
            url = result.get("href", "")
            summary = result.get("body", "")[:300]

            output.append(
                f"SOURCE {number}\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Summary: {summary}"
            )

        return "\n\n".join(output)
