from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, Any

from langgraph.graph import add_messages
from typing_extensions import Annotated


import operator


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    target_url: str
    site_tree: list[str]
    critical_pages: list[str]
    page_contents: Annotated[list[dict[str, str]], operator.add]
    narrative_report: str
    
    # Frontend Compatibility
    initial_search_query_count: int
    max_research_loops: int
    reasoning_model: str
    
    # Internal State
    research_loop_count: int
    evaluation_result: str
    triage_rationale: str


class UrlExtractionState(TypedDict):
    target_url: str


class DiscoveryState(TypedDict):
    site_tree: list[str]


class TriageState(TypedDict):
    critical_pages: list[str]
    triage_rationale: str


class ScrapeState(TypedDict):
    target_url: str
    id: str


class ScrapeOutputState(TypedDict):
    page_contents: list[dict[str, str]]


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report
