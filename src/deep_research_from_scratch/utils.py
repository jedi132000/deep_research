
"""Research Utilities and Tools.

This module provides search and content processing utilities for the research agent,
including web search capabilities and content summarization tools.
"""

from pathlib import Path
from datetime import datetime
from typing_extensions import Annotated, List, Literal

from langchain.chat_models import init_chat_model 
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg
from tavily import TavilyClient

from deep_research_from_scratch.state_research import Summary
from deep_research_from_scratch.prompts import summarize_webpage_prompt
from deep_research_from_scratch.cost_tracker import cost_tracker

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

def get_current_dir() -> Path:
    """Get the current directory of the module.

    This function is compatible with Jupyter notebooks and regular Python scripts.

    Returns:
        Path object representing the current directory
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:  # __file__ is not defined
        return Path.cwd()

# ===== CONFIGURATION =====

summarization_model = init_chat_model(model="openai:gpt-4o-mini")
tavily_client = TavilyClient()

# ===== SEARCH FUNCTIONS =====

def tavily_search_multiple(
    search_queries: List[str], 
    max_results: int = 3, 
    topic: Literal["general", "news", "finance"] = "general", 
    include_raw_content: bool = True, 
) -> List[dict]:
    """Perform search using Tavily API for multiple queries.

    Args:
        search_queries: List of search queries to execute
        max_results: Maximum number of results per query
        topic: Topic filter for search results
        include_raw_content: Whether to include raw webpage content

    Returns:
        List of search result dictionaries
    """
    
    # Execute searches sequentially. Note: yon can use AsyncTavilyClient to parallelize this step.
    search_docs = []
    for query in search_queries:
        result = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic
        )
        search_docs.append(result)

    return search_docs

def summarize_webpage_content(webpage_content: str) -> str:
    """Summarize webpage content using the configured summarization model.
    
    Args:
        webpage_content: Raw webpage content to summarize
        
    Returns:
        Formatted summary with key excerpts
    """
    try:
        # Set up structured output model for summarization
        structured_model = summarization_model.with_structured_output(Summary)
        
        # Generate summary
        summary = structured_model.invoke([
            HumanMessage(content=summarize_webpage_prompt.format(
                webpage_content=webpage_content, 
                date=get_today_str()
            ))
        ])
        
        # Format summary with clear structure
        formatted_summary = (
            f"<summary>\n{summary.summary}\n</summary>\n\n"
            f"<key_excerpts>\n{summary.key_excerpts}\n</key_excerpts>"
        )
        
        return formatted_summary
        
    except Exception as e:
        print(f"Failed to summarize webpage: {str(e)}")
        return webpage_content[:1000] + "..." if len(webpage_content) > 1000 else webpage_content

def enhance_query_for_academic_research(query: str, academic_mode: dict) -> str:
    """Enhance search query with academic-specific patterns and site filters.
    
    Args:
        query: Original search query
        academic_mode: Dictionary containing academic settings
        
    Returns:
        Enhanced query optimized for academic sources
    """
    if not academic_mode or not academic_mode.get("enabled", False):
        return query
    
    academic_level = academic_mode.get("academic_level", "Undergraduate")
    
    # Academic site filters - prioritize scholarly sources
    academic_sites = [
        "site:arxiv.org",
        "site:scholar.google.com", 
        "site:pubmed.ncbi.nlm.nih.gov",
        "site:jstor.org",
        "site:ieee.org",
        "site:acm.org",
        "site:nature.com",
        "site:science.org",
        "site:springer.com",
        "site:elsevier.com",
        "site:wiley.com",
        "site:tandfonline.com"
    ]
    
    # Academic keywords to prioritize scholarly content
    academic_keywords = {
        "Undergraduate": ["study", "research", "analysis", "review"],
        "Graduate": ["research", "analysis", "systematic review", "meta-analysis", "empirical"],
        "PhD/Research": ["peer-reviewed", "systematic review", "meta-analysis", "longitudinal study", "experimental"],
        "Professional": ["evidence-based", "best practices", "systematic review", "clinical"]
    }
    
    # File type filters for academic documents
    academic_filetypes = ["filetype:pdf", "filetype:doc", "filetype:docx"]
    
    # Build enhanced query
    site_filter = " OR ".join(academic_sites[:6])  # Use top 6 academic sites
    keywords = " ".join(academic_keywords.get(academic_level, academic_keywords["Undergraduate"]))
    filetype_filter = " OR ".join(academic_filetypes)
    
    enhanced_query = f"{query} ({site_filter}) {keywords} ({filetype_filter})"
    
    return enhanced_query

def assess_source_quality(url: str, title: str, content: str) -> dict:
    """Assess the academic quality and credibility of a source.
    
    Args:
        url: Source URL
        title: Source title
        content: Source content
        
    Returns:
        Dictionary with quality assessment metrics
    """
    quality_score = 0
    quality_indicators = []
    source_type = "general"
    
    # High-quality academic domains
    high_quality_domains = {
        "arxiv.org": {"score": 9, "type": "preprint", "indicator": "ArXiv preprint server"},
        "pubmed.ncbi.nlm.nih.gov": {"score": 10, "type": "peer-reviewed", "indicator": "PubMed indexed journal"},
        "nature.com": {"score": 10, "type": "peer-reviewed", "indicator": "Nature Publishing"},
        "science.org": {"score": 10, "type": "peer-reviewed", "indicator": "Science journal"},
        "ieee.org": {"score": 9, "type": "peer-reviewed", "indicator": "IEEE publication"},
        "acm.org": {"score": 9, "type": "peer-reviewed", "indicator": "ACM publication"},
        "springer.com": {"score": 8, "type": "peer-reviewed", "indicator": "Springer journal"},
        "elsevier.com": {"score": 8, "type": "peer-reviewed", "indicator": "Elsevier journal"},
        "jstor.org": {"score": 9, "type": "peer-reviewed", "indicator": "JSTOR academic archive"},
        "wiley.com": {"score": 8, "type": "peer-reviewed", "indicator": "Wiley journal"},
        "tandfonline.com": {"score": 8, "type": "peer-reviewed", "indicator": "Taylor & Francis journal"}
    }
    
    # Check domain quality
    for domain, info in high_quality_domains.items():
        if domain in url.lower():
            quality_score = info["score"]
            source_type = info["type"]
            quality_indicators.append(info["indicator"])
            break
    
    # Additional quality indicators in content/title
    content_lower = (content + " " + title).lower()
    
    quality_patterns = {
        "peer-reviewed": 2,
        "peer reviewed": 2,
        "systematic review": 3,
        "meta-analysis": 3,
        "longitudinal study": 2,
        "randomized controlled": 3,
        "doi:": 2,
        "pmid:": 2,
        "abstract": 1,
        "methodology": 1,
        "results": 1,
        "conclusion": 1,
        "references": 1,
        "bibliography": 1
    }
    
    for pattern, score in quality_patterns.items():
        if pattern in content_lower:
            quality_score += score
            quality_indicators.append(f"Contains '{pattern}'")
    
    # PDF bonus (academic papers often in PDF)
    if url.lower().endswith('.pdf'):
        quality_score += 1
        quality_indicators.append("PDF document")
    
    return {
        "quality_score": min(quality_score, 10),  # Cap at 10
        "source_type": source_type,
        "quality_indicators": quality_indicators,
        "is_academic": quality_score >= 5
    }

def deduplicate_search_results(search_results: List[dict]) -> dict:
    """Deduplicate search results by URL to avoid processing duplicate content.
    
    Args:
        search_results: List of search result dictionaries
        
    Returns:
        Dictionary mapping URLs to unique results
    """
    unique_results = {}
    
    for response in search_results:
        for result in response['results']:
            url = result['url']
            if url not in unique_results:
                unique_results[url] = result
    
    return unique_results

def process_search_results(unique_results: dict) -> dict:
    """Process search results by summarizing content where available.
    
    Args:
        unique_results: Dictionary of unique search results
        
    Returns:
        Dictionary of processed results with summaries
    """
    summarized_results = {}
    
    for url, result in unique_results.items():
        # Use existing content if no raw content for summarization
        if not result.get("raw_content"):
            content = result['content']
        else:
            # Summarize raw content for better processing
            content = summarize_webpage_content(result['raw_content'])
        
        summarized_results[url] = {
            'title': result['title'],
            'content': content
        }
    
    return summarized_results

def format_search_output(summarized_results: dict) -> str:
    """Format search results into a well-structured string output.
    
    Args:
        summarized_results: Dictionary of processed search results
        
    Returns:
        Formatted string of search results with clear source separation
    """
    if not summarized_results:
        return "No valid search results found. Please try different search queries or use a different search API."
    
    formatted_output = "Search results: \n\n"
    
    for i, (url, result) in enumerate(summarized_results.items(), 1):
        formatted_output += f"\n\n--- SOURCE {i}: {result['title']} ---\n"
        formatted_output += f"URL: {url}\n\n"
        formatted_output += f"SUMMARY:\n{result['content']}\n\n"
        formatted_output += "-" * 80 + "\n"
    
    return formatted_output

# ===== RESEARCH TOOLS =====

@tool
def tavily_search(
    query: Annotated[str, "The search query to use"],
    max_results: Annotated[int, "Maximum number of search results to return"] = 3,
    include_raw_content: Annotated[bool, "Include raw webpage content in results"] = False,
    topic: Annotated[Literal["general", "news"], "Search topic category"] = "general",
    config: Annotated[RunnableConfig | None, InjectedToolArg] = None
) -> str:
    """Search for information using Tavily search engine with automatic academic enhancement.

    Args:
        query: The search query to execute
        max_results: Maximum number of results to return (default: 3)
        include_raw_content: Whether to include full webpage content (default: False)
        topic: Search topic - "general" for web search, "news" for recent news (default: "general")
        config: Langchain configuration (auto-injected)

    Returns:
        Formatted search results with titles, URLs, content, and quality assessments
    """
    try:
        # Detect if this is an academic search based on query content
        is_academic_query = any(term in query.lower() for term in [
            'academic', 'research', 'study', 'peer-reviewed', 'journal', 'paper',
            'citation', 'scholarly', 'university', 'systematic review', 'meta-analysis',
            'site:arxiv.org', 'site:scholar.google.com', 'filetype:pdf'
        ])
        
        # Track the search operation for cost analysis
        cost_tracker.track_tavily_search(1)
        
        result = tavily_client.search(
            query=query,
            max_results=max_results * 2 if is_academic_query else max_results,  # Get more results for academic filtering
            include_raw_content=include_raw_content,
            topic=topic
        )

        if not result or 'results' not in result:
            return "No search results found."

        results_with_quality = []
        
        # Assess quality of each result
        for item in result['results']:
            title = item.get('title', 'No title')
            url = item.get('url', 'No URL')
            content = item.get('content', 'No content available')
            
            # Use raw content if available and requested
            if include_raw_content and 'raw_content' in item:
                content = summarize_webpage_content(item['raw_content'])
            
            # Assess source quality
            quality_assessment = assess_source_quality(url, title, content)
            
            results_with_quality.append({
                'title': title,
                'url': url,
                'content': content,
                'quality': quality_assessment
            })
        
        # Sort by quality score if academic query detected
        if is_academic_query:
            results_with_quality.sort(key=lambda x: x['quality']['quality_score'], reverse=True)
            # Prioritize academic sources if enough are found
            academic_results = [r for r in results_with_quality if r['quality']['is_academic']]
            if len(academic_results) >= 2:
                results_with_quality = academic_results
        
        # Format results
        formatted_results = []
        for i, item in enumerate(results_with_quality[:max_results], 1):
            quality_info = ""
            if is_academic_query:
                quality = item['quality']
                quality_info = f"\n   📊 **Quality Score**: {quality['quality_score']}/10 ({quality['source_type']})\n   ✅ **Academic Indicators**: {', '.join(quality['quality_indicators'][:3]) if quality['quality_indicators'] else 'General source'}"
            
            formatted_results.append(
                f"{i}. **{item['title']}**\n   URL: {item['url']}{quality_info}\n   Content: {item['content']}\n"
            )
        
        # Add academic header if academic query detected
        header = ""
        if is_academic_query:
            header = "🎓 **Academic-Enhanced Search Results**\n\n"

        return header + "\n".join(formatted_results)

    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def academic_search_helper(
    topic: Annotated[str, "The academic topic to search for"],
    academic_level: Annotated[str, "Academic level: Undergraduate, Graduate, PhD/Research, or Professional"] = "Graduate",
    citation_style: Annotated[str, "Citation style: APA, MLA, Chicago, IEEE, or Harvard"] = "APA"
) -> str:
    """Generate optimized search queries for academic research with source quality guidance.
    
    Args:
        topic: The academic topic to research
        academic_level: Target academic level for appropriate depth
        citation_style: Preferred citation style
        
    Returns:
        Formatted guidance for academic searching including optimized queries
    """
    
    # Generate academic search queries
    base_queries = [
        f"{topic} peer-reviewed systematic review",
        f"{topic} research study academic journal",
        f"{topic} (site:arxiv.org OR site:scholar.google.com OR site:pubmed.ncbi.nlm.nih.gov)",
        f"{topic} filetype:pdf academic paper",
        f'"{topic}" meta-analysis OR "longitudinal study"'
    ]
    
    # Academic level specific guidance
    level_guidance = {
        "Undergraduate": "Focus on review articles, textbooks, and introductory research papers",
        "Graduate": "Prioritize peer-reviewed journals, systematic reviews, and empirical studies", 
        "PhD/Research": "Emphasize recent publications, primary sources, and methodological papers",
        "Professional": "Include evidence-based practices, clinical guidelines, and industry standards"
    }
    
    # Citation style reminders
    citation_reminders = {
        "APA": "Include (Author, Year) format and DOI when available",
        "MLA": "Use (Author Page#) format and include publication details",
        "Chicago": "Use footnotes/endnotes with full publication information", 
        "IEEE": "Use [1] format with full reference list",
        "Harvard": "Use (Author Year) format with complete bibliography"
    }
    
    guidance = f"""🎓 **Academic Research Guidance for: {topic}**

**Recommended Search Queries:**
{chr(10).join(f"• {query}" for query in base_queries)}

**Academic Level ({academic_level}):**
{level_guidance.get(academic_level, level_guidance["Graduate"])}

**Citation Style ({citation_style}):**
{citation_reminders.get(citation_style, citation_reminders["APA"])}

**Quality Indicators to Look For:**
• Peer-reviewed journals and conferences
• University or research institution sources (.edu, .ac.uk)
• DOI numbers and PMID identifiers
• Abstract, methodology, results, conclusion sections
• Recent publication dates (last 5-10 years unless historical research)
• High citation counts on Google Scholar

**Recommended Academic Databases:**
• ArXiv (preprints): arxiv.org
• PubMed (biomedical): pubmed.ncbi.nlm.nih.gov  
• Google Scholar: scholar.google.com
• JSTOR (academic archive): jstor.org
• IEEE (engineering): ieee.org
• ACM (computing): acm.org

Use these optimized queries in your tavily_search calls for better academic results."""

    return guidance


@tool
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.
    
    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.
    
    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?
    
    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?
    
    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps
    """
    return f"Reflection recorded: {reflection}"
