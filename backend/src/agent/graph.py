import os
import requests
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from agent.tools_and_schemas import TargetUrlExtraction, CriticalPages, EvaluateResearch
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client

from agent.state import (
    OverallState,
    UrlExtractionState,
    DiscoveryState,
    TriageState,
    ScrapeState,
    ScrapeOutputState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    url_extraction_instructions,
    triage_instructions,
    narrative_analysis_instructions,
    evaluate_research_instructions,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.utils import get_research_topic, robust_scrape

load_dotenv()

if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")


def extract_url(state: OverallState, config: RunnableConfig) -> UrlExtractionState:
    configurable = Configuration.from_runnable_config(config)
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(TargetUrlExtraction)
    
    formatted_prompt = url_extraction_instructions.format(
        user_query=get_research_topic(state["messages"])
    )
    result = structured_llm.invoke(formatted_prompt)
    return {"target_url": result.url}


def discovery(state: OverallState, config: RunnableConfig) -> DiscoveryState:
    target_url = state["target_url"]
    
    # Prepend https if not there
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    try:
        response = robust_scrape(target_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        parsed_target = urlparse(target_url)
        base_netloc = parsed_target.netloc
        
        ignored_domains = {"facebook.com", "x.com", "twitter.com", "instagram.com", "youtube.com", "linkedin.com", "tiktok.com", "github.com", "vimeo.com", "medium.com", "apple.com", "google.com"}
        
        internal_links = []
        external_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            # Ignore empty or javascript links
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                continue
                
            full_url = urljoin(target_url, href)
            parsed_href = urlparse(full_url)
            clean_url = full_url.split('#')[0]
            
            # Ensure it is a valid http link
            if parsed_href.scheme not in ('http', 'https'):
                continue
                
            domain_parts = parsed_href.netloc.lower().split('.')
            if len(domain_parts) >= 2:
                base_domain = f"{domain_parts[-2]}.{domain_parts[-1]}"
            else:
                base_domain = parsed_href.netloc.lower()
                
            if base_domain in ignored_domains:
                continue
            
            # Categorize as internal (same domain/subdomain) or external
            if base_netloc in parsed_href.netloc:
                if clean_url not in internal_links:
                    internal_links.append(clean_url)
            else:
                if clean_url not in external_links:
                    external_links.append(clean_url)
                    
        # Limit to 50 to avoid prompt explosion (~35 internal, 15 external)
        internal_subset = internal_links[:35]
        external_subset = external_links[:15]
        site_tree = internal_subset + external_subset
    except Exception as e:
        site_tree = [target_url]
        print(f"Discovery error: {e}")
        
    return {"site_tree": site_tree}


def triage(state: OverallState, config: RunnableConfig) -> TriageState:
    configurable = Configuration.from_runnable_config(config)
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(CriticalPages)
    
    formatted_prompt = triage_instructions.format(
        target_url=state["target_url"],
        site_tree="\\n".join(state["site_tree"])
    )
    
    result = structured_llm.invoke(formatted_prompt)
    return {
        "critical_pages": result.pages,
        "triage_rationale": result.rationale
    }


def continue_to_scrape(state: OverallState):
    return [
        Send("scrape_page", {"target_url": page_url, "id": str(idx)})
        for idx, page_url in enumerate(state["critical_pages"])
    ]


def scrape_page(state: ScrapeState, config: RunnableConfig) -> ScrapeOutputState:
    url = state["target_url"]
    try:
        response = robust_scrape(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        # return up to 5000 chars per page
        text = text[:5000]
    except Exception as e:
        text = f"Error scraping page: {str(e)}"
        
    return {"page_contents": [{"url": url, "text": text}]}


def evaluate_research(state: OverallState, config: RunnableConfig) -> OverallState:
    configurable = Configuration.from_runnable_config(config)
    
    loop_count = state.get("research_loop_count", 0)
    max_loops = state.get("max_research_loops", 1)  # Using 1 as default extra loop
    
    if loop_count >= max_loops:
        return {
            "evaluation_result": "Max research loops reached.",
            "research_loop_count": max_loops + 1
        }
        
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(EvaluateResearch)
    
    scraped_content = ""
    scraped_urls = []
    for page in state.get("page_contents", []):
        scraped_content += f"=== URL: {page['url']} ===\\n{page['text'][:2000]}...\\n\\n" # trim to avoid massive prompts
        scraped_urls.append(page['url'])
        
    unscraped_links = [link for link in state.get("site_tree", []) if link not in scraped_urls]
    
    # Cap unscraped links length
    unscraped_links_str = "\\n".join(unscraped_links[:50])
        
    formatted_prompt = evaluate_research_instructions.format(
        target_url=state["target_url"],
        scraped_content=scraped_content,
        unscraped_links=unscraped_links_str
    )
    
    result = structured_llm.invoke(formatted_prompt)
    
    if result.needs_more_research and result.new_target_urls:
        return {
            "evaluation_result": result.reasoning,
            "research_loop_count": loop_count + 1,
            "critical_pages": result.new_target_urls
        }
    else:
        return {
            "evaluation_result": result.reasoning,
            "research_loop_count": max_loops + 1  # Force route skip
        }

def route_after_evaluation(state: OverallState):
    loop_count = state.get("research_loop_count", 0)
    max_loops = state.get("max_research_loops", 1)
    
    if 0 < loop_count <= max_loops:
        return [
            Send("scrape_page", {"target_url": page_url, "id": f"loop_{loop_count}_{idx}"})
            for idx, page_url in enumerate(state["critical_pages"])
        ]
    
    return "analyze_narrative"


def analyze_narrative(state: OverallState, config: RunnableConfig) -> OverallState:
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model
    
    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=0.2,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    # Format the scraped content properly
    scraped_content = ""
    for page in state["page_contents"]:
        scraped_content += f"=== URL: {page['url']} ===\\n{page['text']}\\n\\n"
        
    formatted_prompt = narrative_analysis_instructions.format(
        current_date=get_current_date(),
        target_url=state["target_url"],
        scraped_content=scraped_content,
    )
    
    result = llm.invoke(formatted_prompt)
    
    return {
        "messages": [AIMessage(content=result.content)],
        "narrative_report": result.content
    }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("extract_url", extract_url)
builder.add_node("discovery", discovery)
builder.add_node("triage", triage)
builder.add_node("scrape_page", scrape_page)
builder.add_node("evaluate_research", evaluate_research)
builder.add_node("analyze_narrative", analyze_narrative)

# Set the entrypoint
builder.add_edge(START, "extract_url")
builder.add_edge("extract_url", "discovery")
builder.add_edge("discovery", "triage")

# Add conditional edge to continue with scrape queries in a parallel branch
builder.add_conditional_edges(
    "triage", continue_to_scrape, ["scrape_page"]
)

# After scraping finishes, evaluate research (fan-in from parallel scrape)
builder.add_edge("scrape_page", "evaluate_research")

# Conditional routing after evaluation
builder.add_conditional_edges(
    "evaluate_research", route_after_evaluation, ["scrape_page", "analyze_narrative"]
)

builder.add_edge("analyze_narrative", END)

graph = builder.compile(name="org-narrative-agent")
