"""Cost Tracking and Estimation Module.

This module provides real-time cost tracking for AI model usage across different research modes,
including token counting and USD cost calculation based on current model pricing.
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ModelUsage:
    """Track usage for a single model call."""
    model_name: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    operation: str  # e.g., "search", "summarize", "compress", "think"

@dataclass 
class CostSession:
    """Track costs for an entire research session."""
    session_id: str
    research_mode: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    model_calls: List[ModelUsage] = field(default_factory=list)
    
    @property
    def total_input_tokens(self) -> int:
        return sum(call.input_tokens for call in self.model_calls)
    
    @property
    def total_output_tokens(self) -> int:
        return sum(call.output_tokens for call in self.model_calls)
    
    @property
    def total_cost_usd(self) -> float:
        return sum(call.cost_usd for call in self.model_calls)
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

class CostTracker:
    """Real-time cost tracking for Deep Research operations."""
    
    # Current model pricing (USD per 1K tokens) - Updated Dec 2024
    MODEL_PRICING = {
        "openai:gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "openai:gpt-4o": {"input": 0.0025, "output": 0.010},
        "openai:gpt-4.1": {"input": 0.03, "output": 0.06},
        "openai:gpt-4.1-mini": {"input": 0.0015, "output": 0.006},
        "anthropic:claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
        "anthropic:claude-haiku-4": {"input": 0.0008, "output": 0.004},
        "tavily:search": {"per_search": 0.005},  # Estimated per search cost
    }
    
    def __init__(self):
        self.current_session: Optional[CostSession] = None
        self.session_history: List[CostSession] = []
    
    def start_session(self, research_mode: str, query: str) -> str:
        """Start a new cost tracking session."""
        session_id = f"session_{int(time.time())}"
        self.current_session = CostSession(
            session_id=session_id,
            research_mode=research_mode,
            query=query,
            start_time=datetime.now()
        )
        return session_id
    
    def end_session(self) -> Optional[CostSession]:
        """End the current session and return cost summary."""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            completed_session = self.current_session
            self.session_history.append(completed_session)
            self.current_session = None
            return completed_session
        return None
    
    def track_model_call(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int, 
        operation: str = "unknown"
    ) -> ModelUsage:
        """Track a single model API call."""
        cost_usd = self.calculate_cost(model_name, input_tokens, output_tokens)
        
        usage = ModelUsage(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            timestamp=datetime.now(),
            operation=operation
        )
        
        if self.current_session:
            self.current_session.model_calls.append(usage)
        
        return usage
    
    def track_tavily_search(self, num_searches: int = 1) -> ModelUsage:
        """Track Tavily search API calls."""
        cost_per_search = self.MODEL_PRICING.get("tavily:search", {}).get("per_search", 0.005)
        total_cost = cost_per_search * num_searches
        
        usage = ModelUsage(
            model_name="tavily:search",
            input_tokens=0,  # Tavily doesn't use token-based pricing
            output_tokens=0,
            cost_usd=total_cost,
            timestamp=datetime.now(),
            operation="web_search"
        )
        
        if self.current_session:
            self.current_session.model_calls.append(usage)
        
        return usage
    
    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate USD cost for a model call."""
        pricing = self.MODEL_PRICING.get(model_name, {"input": 0.001, "output": 0.002})
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def estimate_research_cost(self, research_mode: str, query_length: int) -> Dict[str, float]:
        """Estimate costs for different research modes before execution."""
        
        # Base estimates based on typical usage patterns
        estimates = {
            "Basic Research": {
                "searches": 2,
                "search_calls": 3,  # LLM calls for search planning
                "summarization_calls": 4,  # Content processing
                "compression_calls": 1,
                "input_tokens_per_call": 1500,
                "output_tokens_per_call": 800
            },
            "MCP Research": {
                "searches": 0,
                "search_calls": 2,
                "summarization_calls": 3,
                "compression_calls": 1,
                "input_tokens_per_call": 2000,
                "output_tokens_per_call": 1000
            },
            "Enhanced MCP Research": {
                "searches": 1,
                "search_calls": 4,
                "summarization_calls": 6,
                "compression_calls": 1,
                "input_tokens_per_call": 2500,
                "output_tokens_per_call": 1200
            },
            "Full Research": {
                "searches": 3,
                "search_calls": 6,
                "summarization_calls": 8,
                "compression_calls": 2,
                "input_tokens_per_call": 3000,
                "output_tokens_per_call": 1500
            }
        }
        
        mode_estimate = estimates.get(research_mode, estimates["Basic Research"])
        
        # Calculate total estimated cost
        total_llm_calls = (
            mode_estimate["search_calls"] + 
            mode_estimate["summarization_calls"] + 
            mode_estimate["compression_calls"]
        )
        
        # Use current optimized models for Basic Research
        if research_mode == "Basic Research":
            model_cost = self.calculate_cost(
                "openai:gpt-4o-mini",
                total_llm_calls * mode_estimate["input_tokens_per_call"],
                total_llm_calls * mode_estimate["output_tokens_per_call"]
            )
        else:
            model_cost = self.calculate_cost(
                "anthropic:claude-sonnet-4-20250514", 
                total_llm_calls * mode_estimate["input_tokens_per_call"],
                total_llm_calls * mode_estimate["output_tokens_per_call"]
            )
        
        search_cost = mode_estimate["searches"] * 0.005
        
        return {
            "estimated_total_usd": model_cost + search_cost,
            "estimated_input_tokens": total_llm_calls * mode_estimate["input_tokens_per_call"],
            "estimated_output_tokens": total_llm_calls * mode_estimate["output_tokens_per_call"],
            "estimated_searches": mode_estimate["searches"],
            "model_cost_usd": model_cost,
            "search_cost_usd": search_cost
        }
    
    def get_session_summary(self) -> Optional[Dict]:
        """Get current session cost summary."""
        if not self.current_session:
            return None
        
        return {
            "session_id": self.current_session.session_id,
            "research_mode": self.current_session.research_mode,
            "query": self.current_session.query[:100] + "..." if len(self.current_session.query) > 100 else self.current_session.query,
            "duration_seconds": self.current_session.duration_seconds,
            "total_input_tokens": self.current_session.total_input_tokens,
            "total_output_tokens": self.current_session.total_output_tokens,
            "total_cost_usd": self.current_session.total_cost_usd,
            "model_calls_count": len(self.current_session.model_calls),
            "cost_breakdown": [
                {
                    "model": call.model_name,
                    "operation": call.operation,
                    "input_tokens": call.input_tokens,
                    "output_tokens": call.output_tokens,
                    "cost_usd": call.cost_usd
                }
                for call in self.current_session.model_calls
            ]
        }
    
    def get_daily_summary(self) -> Dict:
        """Get today's usage summary."""
        today = datetime.now().date()
        today_sessions = [
            session for session in self.session_history 
            if session.start_time.date() == today
        ]
        
        if not today_sessions:
            return {"total_cost_usd": 0, "total_sessions": 0, "total_tokens": 0}
        
        return {
            "total_cost_usd": sum(session.total_cost_usd for session in today_sessions),
            "total_input_tokens": sum(session.total_input_tokens for session in today_sessions),
            "total_output_tokens": sum(session.total_output_tokens for session in today_sessions),
            "total_sessions": len(today_sessions),
            "average_cost_per_session": sum(session.total_cost_usd for session in today_sessions) / len(today_sessions),
            "mode_breakdown": self._get_mode_breakdown(today_sessions)
        }
    
    def _get_mode_breakdown(self, sessions: List[CostSession]) -> Dict[str, Dict]:
        """Get cost breakdown by research mode."""
        breakdown = {}
        for session in sessions:
            mode = session.research_mode
            if mode not in breakdown:
                breakdown[mode] = {
                    "sessions": 0,
                    "total_cost": 0,
                    "total_tokens": 0
                }
            breakdown[mode]["sessions"] += 1
            breakdown[mode]["total_cost"] += session.total_cost_usd
            breakdown[mode]["total_tokens"] += session.total_input_tokens + session.total_output_tokens
        
        return breakdown

# Global cost tracker instance
cost_tracker = CostTracker()