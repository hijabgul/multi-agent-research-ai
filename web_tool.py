```python
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ddgs import DDGS


# ============================================================
# TOOL INPUT SCHEMA
# ============================================================

class WebResearchInput(BaseModel):

    query: str = Field(
        ...,
        description=(
            "The exact web search query to search for. "
            "Example: latest impacts of artificial intelligence on education"
        )
    )


# ============================================================
# WEB RESEARCH TOOL
# ============================================================

class WebResearchTool(BaseTool):

    name: str = "web_research_tool"

    description: str = (
        "Search the internet for current information. "
        "Use this tool when you need web sources, facts, "
        "recent information, or supporting evidence. "
        "The input must contain only a search query."
    )

    args_schema: Type[BaseModel] = WebResearchInput

    # --------------------------------------------------------
    # TOOL FUNCTION
    # --------------------------------------------------------

    def _run(self, query: str) -> str:

        query = query.strip()

        if not query:

            return "No search query was provided."

        try:

            # Search only a small number of results
            # to keep the agent efficient.

            results = DDGS().text(
                query,
                max_results=5
            )

        except Exception as e:

            return (
                "Web search failed. "
                f"Error: {str(e)}"
            )

        if not results:

            return (
                f"No web results were found for: {query}"
            )

        output = []

        for number, result in enumerate(results, start=1):

            title = result.get(
                "title",
                "Untitled"
            )

            url = result.get(
                "href",
                ""
            )

            body = result.get(
                "body",
                ""
            )

            # Keep snippets short.
            body = body[:500]

            output.append(
                f"""
SOURCE {number}

Title:
{title}

URL:
{url}

Summary:
{body}
""".strip()
            )

        return "\n\n".join(output)
```
