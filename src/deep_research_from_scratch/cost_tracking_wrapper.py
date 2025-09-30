"""Cost Tracking Wrapper for Research Agents.

This module provides decorators and utilities to automatically track
API costs during research operations.
"""

import functools
import time
from typing import Any, Callable, Dict
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from .cost_tracker import cost_tracker


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 characters ≈ 1 token for GPT models)."""
    return max(1, len(text) // 4)

def extract_message_content(messages) -> str:
    """Extract text content from various message formats."""
    if isinstance(messages, list):
        content = ""
        for msg in messages:
            if hasattr(msg, 'content'):
                content += str(msg.content) + " "
            elif isinstance(msg, dict) and 'content' in msg:
                content += str(msg['content']) + " "
            else:
                content += str(msg) + " "
        return content.strip()
    elif hasattr(messages, 'content'):
        return str(messages.content)
    elif isinstance(messages, dict):
        return str(messages.get('content', messages))
    else:
        return str(messages)

def track_model_usage(model_name: str, operation: str = "unknown"):
    """Decorator to track model API usage."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract input content for token estimation
            input_content = ""
            if args:
                input_content = extract_message_content(args[0])
            
            input_tokens = estimate_tokens(input_content)
            
            # Execute the function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Extract output content for token estimation
            output_content = extract_message_content(result)
            output_tokens = estimate_tokens(output_content)
            
            # Track the usage
            try:
                cost_tracker.track_model_call(
                    model_name=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    operation=operation
                )
            except Exception as e:
                # Don't break the main function if cost tracking fails
                print(f"Cost tracking error: {e}")
            
            return result
        return wrapper
    return decorator

def track_async_model_usage(model_name: str, operation: str = "unknown"):
    """Decorator to track async model API usage."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract input content for token estimation
            input_content = ""
            if args:
                input_content = extract_message_content(args[0])
            
            input_tokens = estimate_tokens(input_content)
            
            # Execute the function
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Extract output content for token estimation
            output_content = extract_message_content(result)
            output_tokens = estimate_tokens(output_content)
            
            # Track the usage
            try:
                cost_tracker.track_model_call(
                    model_name=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    operation=operation
                )
            except Exception as e:
                # Don't break the main function if cost tracking fails
                print(f"Cost tracking error: {e}")
            
            return result
        return wrapper
    return decorator

class CostTrackingModel:
    """Wrapper for LangChain models to automatically track costs."""
    
    def __init__(self, model: Runnable, model_name: str):
        self.model = model
        self.model_name = model_name
        
    def invoke(self, input_data, **kwargs):
        """Track synchronous model invocation."""
        input_content = extract_message_content(input_data)
        input_tokens = estimate_tokens(input_content)
        
        result = self.model.invoke(input_data, **kwargs)
        
        output_content = extract_message_content(result)
        output_tokens = estimate_tokens(output_content)
        
        try:
            cost_tracker.track_model_call(
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                operation="model_invoke"
            )
        except Exception as e:
            print(f"Cost tracking error: {e}")
        
        return result
    
    async def ainvoke(self, input_data, **kwargs):
        """Track asynchronous model invocation."""
        input_content = extract_message_content(input_data)
        input_tokens = estimate_tokens(input_content)
        
        result = await self.model.ainvoke(input_data, **kwargs)
        
        output_content = extract_message_content(result)
        output_tokens = estimate_tokens(output_content)
        
        try:
            cost_tracker.track_model_call(
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                operation="model_ainvoke"
            )
        except Exception as e:
            print(f"Cost tracking error: {e}")
        
        return result
    
    def __getattr__(self, name):
        """Delegate other attributes to the wrapped model."""
        return getattr(self.model, name)

def track_tavily_search(func: Callable) -> Callable:
    """Decorator to track Tavily search API calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Count number of searches (assume 1 search per function call)
        num_searches = 1
        
        result = func(*args, **kwargs)
        
        try:
            cost_tracker.track_tavily_search(num_searches)
        except Exception as e:
            print(f"Cost tracking error: {e}")
        
        return result
    return wrapper

# Quick setup function for existing models
def wrap_model_for_cost_tracking(model: Runnable, model_name: str) -> CostTrackingModel:
    """Wrap an existing model for automatic cost tracking."""
    return CostTrackingModel(model, model_name)