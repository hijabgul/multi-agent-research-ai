from typing import Type

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebResearchInput(BaseModel):
    query: str = Field(
        ...,
        description="The research question or search query."
    )


class WebResearchTool(BaseTool):
    name: str = "Web Research Tool"

    description: str = (
        "Searches the web for current information and extracts "
        "useful content from relevant webpages."
    )

    args_schema: Type[BaseModel] = WebResearchInput

    def _run(self, query: str) -> str:

        try:

            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=5
                    )
                )

            if not results:
                return "No search results found."

            sources = []

            for number, result in enumerate(results, start=1):

                title = result.get(
                    "title",
                    "Untitled"
                )

                url = result.get(
                    "href",
                    ""
                )

                snippet = result.get(
                    "body",
                    ""
                )

                webpage_text = ""

                if url:

                    try:

                        response = requests.get(
                            url,
                            timeout=10,
                            headers={
                                "User-Agent": "Mozilla/5.0"
                            }
                        )

                        if response.ok:

                            soup = BeautifulSoup(
                                response.text,
                                "html.parser"
                            )

                            for tag in soup(
                                [
                                    "script",
                                    "style",
                                    "nav",
                                    "footer"
                                ]
                            ):
                                tag.decompose()

                            webpage_text = soup.get_text(
                                separator=" ",
                                strip=True
                            )

                            webpage_text = webpage_text[:5000]

                    except Exception:
                        webpage_text = ""

                sources.append(
                    f"""
SOURCE {number}

Title:
{title}

URL:
{url}

Search Summary:
{snippet}

Webpage Content:
{webpage_text}
"""
                )

            return "\n".join(sources)

        except Exception as error:

            return (
                "The web research tool encountered an error: "
                f"{error}"
            )
