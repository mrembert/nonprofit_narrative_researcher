from typing import List
from pydantic import BaseModel, Field


class TargetUrlExtraction(BaseModel):
    url: str = Field(
        description="The primary website URL of the organization to analyze."
    )


class CriticalPages(BaseModel):
    pages: List[str] = Field(
        description="A list of 3-5 critical page URLs for analyzing the organizational narrative."
    )
    rationale: str = Field(
        description="A brief explanation of why these pages are most relevant for the narrative."
    )


class EvaluateResearch(BaseModel):
    needs_more_research: bool = Field(
        description="True if the current scraped content is missing critical narrative elements (like funding, history, key team members, recent news) and we have un-scraped links available."
    )
    reasoning: str = Field(
        description="A brief explanation of what is missing or why we have enough information."
    )
    new_target_urls: List[str] = Field(
        description="A list of 1-3 new critical pages to scrape to fill the identified gaps. Must be from the 'Unscraped Links' list."
    )

