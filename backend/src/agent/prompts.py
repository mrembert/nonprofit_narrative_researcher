from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


url_extraction_instructions = """Extract the exact organizational website URL from the user's request.
User Request:
{user_query}
"""

triage_instructions = """You are an expert researcher. Given a target organization URL and a list of internal links discovered on the site, \
your goal is to select the most critical 3 to 5 pages that will best help understand the organization's narrative, story, \
and intended audience.
Please select a mix of both static pages (e.g., "About Us", "Mission", "History", "Our Story") AND dynamic content pages (e.g., "Blog", "News Releases", "Latest updates") to get a comprehensive view of their historical narrative and current active messaging.

Target URL: {target_url}

Discovered Links:
{site_tree}

Select 3-5 most critical links.
"""

narrative_analysis_instructions = """You are an expert qualitative researcher and brand strategist.
Analyze the following text scraped from the organization's key web pages to develop a report on their "organizational narrative."

The report should include:
- The core story the organization tells about itself.
- The implied audiences based on the narrative.
- Key words, phrases, or terminology uniquely or specifically used by the organization.
- Potential areas of narrative tension or inconsistencies in how they present themselves.

The current date is {current_date}.
Use markdown to format the report beautifully. Include citations to the pages you used (by URL) if applicable.

Target Organization: {target_url}

Scraped Pages Content:
{scraped_content}
"""

evaluate_research_instructions = """You are an expert researcher. You have scraped initial content from the organization's website.
Please review the content gathered so far to determine if there are critical missing pieces required to build a comprehensive organizational narrative.
Key narrative elements include:
- The core story/mission
- Funding sources or financial info
- History of the organization
- Key team members / leadership
- Recent news, blogs, or active campaigns

If you have enough information, return `needs_more_research: false`.
If you are missing critical information AND there are unscraped links available that might contain this information, return `needs_more_research: true` and select 1-3 new links to scrape.

Target Organization: {target_url}

Scraped Content So Far:
{scraped_content}

Unscraped Links Available:
{unscraped_links}
"""
