"""Virtual Research Assistant for Query Scoping.

This module provides an intelligent assistant that helps users refine and scope
their research queries for better results across different research modes.
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

@dataclass
class ScopingSuggestion:
    """A scoping suggestion with rationale."""
    original_query: str
    suggested_query: str
    rationale: str
    research_mode: str
    estimated_improvement: str
    keywords: List[str]

class VirtualResearchAssistant:
    """Intelligent assistant for research query scoping and optimization."""
    
    def __init__(self):
        self.model = None  # Lazy initialization
        self.scoping_prompt = self._get_scoping_prompt()
    
    def _ensure_model_loaded(self):
        """Ensure the model is loaded when needed."""
        if self.model is None:
            try:
                self.model = init_chat_model(model="openai:gpt-4o-mini", temperature=0.1)
            except Exception as e:
                print(f"Warning: Could not initialize virtual assistant model: {e}")
                return False
        return True
    
    def _get_scoping_prompt(self) -> str:
        """Get the system prompt for the scoping assistant."""
        return """You are a Virtual Research Assistant specializing in query optimization and scoping. Your job is to help users refine their research queries to get better, more focused results.

ANALYSIS FRAMEWORK:
1. **Query Clarity**: Is the query specific enough or too broad?
2. **Research Mode Fit**: Which research mode would work best?
3. **Keyword Optimization**: What key terms would improve results?
4. **Scope Refinement**: How can we narrow or broaden appropriately?
5. **Expected Outcomes**: What kind of results should the user expect?

RESEARCH MODES AVAILABLE:
- **Basic Research**: Fast web search for current info, news, trends
- **MCP Research**: Local document analysis and file-based research  
- **Enhanced MCP Research**: Local files + statistical data from Data Commons
- **Full Research**: Comprehensive multi-agent analysis with detailed reports

SCOPING STRATEGIES:
- **Too Broad**: Add specific constraints (time, location, industry, etc.)
- **Too Narrow**: Expand scope or suggest related areas
- **Unclear Intent**: Ask clarifying questions or suggest alternatives
- **Mode Mismatch**: Recommend better research mode for the query type

OUTPUT FORMAT:
Provide exactly 3 alternative scopings as JSON:
{
  "suggestions": [
    {
      "original_query": "user's original query",
      "suggested_query": "improved version",
      "rationale": "why this scoping is better",
      "research_mode": "recommended mode",
      "estimated_improvement": "what improvement to expect",
      "keywords": ["key", "terms", "for", "search"]
    }
  ],
  "general_advice": "overall guidance for the user",
  "complexity_score": "1-5 (1=simple, 5=very complex)"
}

Be concise but helpful. Focus on making queries more actionable and results-oriented."""

    def analyze_query(self, query: str) -> Dict:
        """Analyze a query and provide scoping suggestions."""
        if not self._ensure_model_loaded():
            return self._create_fallback_suggestions(query)
            
        try:
            messages = [
                SystemMessage(content=self.scoping_prompt),
                HumanMessage(content=f"""Please analyze this research query and provide 3 scoping suggestions:

QUERY: "{query}"

Consider:
- Is this query too broad, too narrow, or appropriately scoped?
- Which research mode would be most effective?
- What specific improvements would make this query more actionable?
- What keywords or constraints could improve results?

Provide your response in the exact JSON format specified.""")
            ]
            
            response = self.model.invoke(messages)
            
            # Parse the JSON response
            import json
            try:
                result = json.loads(str(response.content))
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._create_fallback_suggestions(query)
                
        except Exception as e:
            print(f"Error in query analysis: {e}")
            return self._create_fallback_suggestions(query)
    
    def _create_fallback_suggestions(self, query: str) -> Dict:
        """Create basic suggestions if AI analysis fails."""
        return {
            "suggestions": [
                {
                    "original_query": query,
                    "suggested_query": f"{query} - recent developments 2024-2025",
                    "rationale": "Adding time constraints for more current results",
                    "research_mode": "Basic Research", 
                    "estimated_improvement": "More recent and relevant information",
                    "keywords": ["recent", "2024", "2025", "latest"]
                },
                {
                    "original_query": query,
                    "suggested_query": f"comprehensive analysis of {query}",
                    "rationale": "Broader scope for thorough coverage", 
                    "research_mode": "Full Research",
                    "estimated_improvement": "More detailed and comprehensive results",
                    "keywords": ["analysis", "comprehensive", "detailed"]
                },
                {
                    "original_query": query,
                    "suggested_query": f"{query} - key statistics and data",
                    "rationale": "Focus on quantitative insights",
                    "research_mode": "Enhanced MCP Research", 
                    "estimated_improvement": "Data-driven insights with statistics",
                    "keywords": ["statistics", "data", "metrics", "numbers"]
                }
            ],
            "general_advice": "Consider adding specific constraints like time period, geography, or industry focus.",
            "complexity_score": "3"
        }
    
    def get_quick_tips(self, query: str) -> List[str]:
        """Get quick scoping tips for a query."""
        query_lower = query.lower()
        tips = []
        
        # Length-based tips
        if len(query.split()) < 3:
            tips.append("💡 Try adding more specific details to your query")
        elif len(query.split()) > 15:
            tips.append("💡 Consider breaking this into multiple focused queries")
        
        # Content-based tips
        if any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            tips.append("🔍 Comparison queries work well with Basic or Full Research modes")
        
        if any(word in query_lower for word in ['trend', 'statistics', 'data', 'numbers']):
            tips.append("📊 Statistical queries are perfect for Enhanced MCP Research")
        
        if any(word in query_lower for word in ['recent', 'latest', 'current', 'news']):
            tips.append("⚡ Current events queries are ideal for Basic Research")
        
        if 'local' in query_lower or 'my' in query_lower:
            tips.append("📁 Local queries work best with MCP Research modes")
        
        # Generic tips if no specific patterns found
        if not tips:
            tips = [
                "🎯 Add specific time periods (e.g., '2024', 'last 5 years')",
                "🌍 Include geographic constraints if relevant", 
                "🏢 Specify industry or domain for business queries"
            ]
        
        return tips[:3]  # Return max 3 tips
    
    def suggest_research_mode(self, query: str) -> Tuple[str, str]:
        """Suggest the best research mode for a query."""
        query_lower = query.lower()
        
        # Statistical/data queries
        if any(word in query_lower for word in ['statistics', 'data', 'trends', 'demographics', 'economic']):
            return "Enhanced MCP Research", "📊 Great for statistical analysis and data-driven insights"
        
        # Current events/news
        if any(word in query_lower for word in ['recent', 'latest', 'current', 'news', 'breaking', '2024', '2025']):
            return "Basic Research", "⚡ Perfect for current information and recent developments"
        
        # Local/document queries  
        if any(word in query_lower for word in ['local', 'my', 'document', 'file', 'report']):
            return "MCP Research", "📁 Ideal for analyzing local documents and files"
        
        # Complex analysis
        if any(word in query_lower for word in ['comprehensive', 'detailed', 'analysis', 'research', 'study']):
            return "Full Research", "🧠 Best for thorough, multi-perspective analysis"
        
        # Default recommendation
        return "Basic Research", "🔍 Good starting point for most queries"

# Global assistant instance
virtual_assistant = VirtualResearchAssistant()