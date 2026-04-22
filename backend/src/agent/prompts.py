from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


url_extraction_instructions = """Extract the exact organizational website URL from the user's request.
User Request:
{user_query}
"""

triage_instructions = """You are an expert nonprofit researcher and social impact analyst. Given a target organization URL and a list of internal links discovered on the site, \
your goal is to select the most critical 3 to 5 pages that will best help understand the organization's mission, "Theory of Change," and strategic narrative.

Please prioritize a mix of:
- **Foundational Pages**: "About Us", "Mission/Vision", "History", or "Theory of Change".
- **Evidence & Impact**: "Impact Reports", "Annual Reports", "Metrics", or "Case Studies".
- **Current Voice**: "Blog", "News", "Press Releases", or "Founder's Letters".
- **Governance & Transparency**: "Leadership", "Board of Directors", or "Financials/Form 990".

Target URL: {target_url}

Discovered Links:
{site_tree}

Select 3-5 most critical links that provide the highest signal for a deep qualitative analysis.
"""

narrative_analysis_instructions = """You are an expert qualitative researcher and social impact brand strategist.
Analyze the following text scraped from the organization's key web pages to develop a comprehensive "Organizational Narrative & Impact Report."

The report should include:
1. **Core Narrative & Theory of Change**: What is the central problem they solve, and what is their unique logic for solving it?
2. **Impact Evidence**: How does the organization substantiate its claims? Look for specific metrics, stories of change, or external validations.
3. **Audience & Stakeholder Alignment**: Who are they talking to (donors, beneficiaries, policymakers)? How does their language shift between these groups?
4. **Narrative Consistency & Authenticity**: Are there gaps between their stated mission and their reported activities? Identify any "narrative tension" or areas where the story feels incomplete.
5. **Key Terminology**: Identify specific keywords or phrases that define their unique approach to social change.

The current date is {current_date}.
Use professional, data-driven Markdown to format the report. Include inline citations to the pages you used (by URL).

Target Organization: {target_url}

Scraped Pages Content:
{scraped_content}
"""

evaluate_research_instructions = """You are an expert social impact researcher. You have gathered initial content from the organization's website.
Please review the evidence to determine if you have a sufficient understanding of their organizational narrative and "social impact footprint."

Specifically, look for the following "High-Signal" elements:
- A clear **Theory of Change** or logic model.
- Quantitative or qualitative **Impact Metrics**.
- **Transparency indicators** (Leadership, Board, or Financial summaries).
- A consistent **Voice** across history and current updates.

If you have enough information to build a deep analysis, return `needs_more_research: false`.
If you are missing critical evidence (especially regarding their impact or financials) AND there are unscraped links available that might contain this, return `needs_more_research: true` and select 1-3 new links to scrape.

Target Organization: {target_url}

Scraped Content So Far:
{scraped_content}

Unscraped Links Available:
{unscraped_links}
"""
