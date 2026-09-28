from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from ddgs import DDGS


class WebResearchInput(BaseModel):
    query: str = Field(
        ...,
        description="The exact web search query to search for."
    )


class WebResearchTool(BaseTool):
    name: str = "web_research_tool"

    description: str = (
        "Search the internet for current information, facts, "
        "recent information, and supporting evidence. "
        "Provide exactly one parameter called query."
    )

    args_schema: Type[BaseModel] = WebResearchInput

    def _run(self, query: str) -> str:

        if not query or not query.strip():
            return "No search query was provided."

        query = query.strip()

        try:
            results = DDGS().text(
                query,
                max_results=5
            )

        except Exception as e:
            return f"Web search failed: {str(e)}"

        if not results:
            return f"No web results found for: {query}"

        output = []

        for number, result in enumerate(results, start=1):

            title = result.get("title", "Untitled")
            url = result.get("href", "")
            summary = result.get("body", "")

            output.append(
                f"""
SOURCE {number}

Title:
{title}

URL:
{url}

Summary:
{summary[:500]}
""".strip()
            )

        return "\n\n".join(output)
