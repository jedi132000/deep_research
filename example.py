#!/usr/bin/env python3
"""
Example usage of the Deep Research Agent as a Python application
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the research functions
from deep_research_from_scratch.main import run_basic_research, run_full_research

async def main():
    """Example usage of different research modes"""
    
    print("🔍 Deep Research Agent - Example Usage\n")
    
    # Example query
    query = "What are the latest trends in artificial intelligence for 2024?"
    
    print(f"Research Query: {query}\n")
    print("=" * 50)
    
    # Check if API keys are available
    if not os.getenv('TAVILY_API_KEY'):
        print("⚠️  TAVILY_API_KEY not found in environment")
        print("Please set up your API keys in a .env file")
        return
    
    if not (os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')):
        print("⚠️  No AI model API keys found")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        return
    
    try:
        # Run basic research
        print("🚀 Running Basic Research...\n")
        basic_result = await run_basic_research(query)
        print("📋 Basic Research Results:")
        print("-" * 30)
        print(basic_result[:500] + "..." if len(basic_result) > 500 else basic_result)
        
        print("\n" + "=" * 50)
        
        # Uncomment to run full research (takes longer)
        # print("🚀 Running Full Multi-Agent Research...\n")
        # full_result = await run_full_research(query)
        # print("📋 Full Research Results:")
        # print("-" * 30)
        # print(full_result[:500] + "..." if len(full_result) > 500 else full_result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your API keys are correctly configured")

if __name__ == "__main__":
    asyncio.run(main())