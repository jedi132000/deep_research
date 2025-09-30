"""Enhanced Research Agent with Data Commons MCP Integration.

This module implements a research agent that integrates with multiple Model Context Protocol (MCP)
servers including filesystem access and Google's Data Commons for public statistical data.

Key features:
- Multi-MCP server integration (filesystem + Data Commons)
- Access to comprehensive public datasets through Data Commons
- Local document research and analysis
- Statistical data analysis and visualization
- Async operations for concurrent tool execution
- Research compression for efficient processing
- Lazy MCP client initialization for LangGraph Platform compatibility
"""

import os

from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END

from .prompts import research_agent_prompt_with_mcp, compress_research_system_prompt, compress_research_human_message
from .state_research import ResearcherState, ResearcherOutputState
from .utils import get_today_str, think_tool, get_current_dir

# ===== ENHANCED MCP CONFIGURATION =====

# Multi-MCP server configuration for filesystem + Data Commons access
enhanced_mcp_config = {
    "filesystem": {
        "command": "npx",
        "args": [
            "-y",  # Auto-install if needed
            "@modelcontextprotocol/server-filesystem",
            str(get_current_dir() / "files")  # Path to research documents
        ],
        "transport": "stdio"  # Communication via stdin/stdout
    },
    "datacommons": {
        "command": "uvx",
        "args": [
            "datacommons-mcp@latest",
            "serve", 
            "stdio"
        ],
        "transport": "stdio",
        "env": {
            "DC_API_KEY": os.getenv("DC_API_KEY", "")  # Data Commons API key from env
        }
    }
}

# Global client variable - will be initialized lazily
_enhanced_client = None

def get_enhanced_mcp_client():
    """Get or initialize enhanced MCP client with Data Commons + filesystem access."""
    global _enhanced_client
    if _enhanced_client is None:
        # Check if Data Commons API key is available
        dc_api_key = os.getenv("DC_API_KEY")
        
        if dc_api_key:
            # Full configuration with Data Commons
            print("🌍 Initializing enhanced MCP client with Data Commons + filesystem access...")
            _enhanced_client = MultiServerMCPClient(enhanced_mcp_config)
        else:
            # Fallback to filesystem only
            print("📁 Data Commons API key not found, using filesystem-only MCP...")
            filesystem_only_config = {"filesystem": enhanced_mcp_config["filesystem"]}
            _enhanced_client = MultiServerMCPClient(filesystem_only_config)
        
        print("✅ Enhanced MCP client initialized successfully")
    
    return _enhanced_client

# Enhanced model configuration
enhanced_model = init_chat_model(model="anthropic:claude-sonnet-4-20250514")

# ===== ENHANCED PROMPTS =====

enhanced_research_agent_prompt_with_mcp = """You are an enhanced research assistant with access to both local files and comprehensive public statistical data through Data Commons. For context, today's date is {date}.

Your capabilities include:
1. **Local File Analysis**: Search, read, and analyze documents in your local files directory
2. **Data Commons Access**: Query vast public datasets including:
   - Economic indicators (GDP, unemployment, inflation)
   - Demographics (population, age distributions, education)
   - Health statistics (disease prevalence, mortality rates, healthcare access)
   - Environmental data (climate, pollution, energy consumption)
   - Social indicators (crime rates, housing, transportation)

**Research Strategy:**
- Start with local files if the query relates to project-specific or proprietary information
- Use Data Commons for statistical data, comparisons, and public information
- Combine both sources for comprehensive analysis when appropriate
- Always cite your sources and specify whether data comes from local files or Data Commons

**Data Commons Query Examples:**
- "What is the GDP growth rate for BRICS nations?"
- "Compare life expectancy across different US states"
- "Show unemployment trends in European countries"
- "Analyze health outcomes by income level"

**Available Tools:**
- File system tools for local document analysis
- Data Commons tools for statistical data retrieval
- Think tool for research planning and reflection

Conduct thorough research using the most appropriate data sources for each query. Provide well-sourced, comprehensive answers with proper citations.
"""

# ===== ENHANCED RESEARCH NODES =====

async def enhanced_researcher_agent(state: ResearcherState) -> ResearcherState:
    """Enhanced research agent with Data Commons + filesystem access."""
    
    # Get MCP client with enhanced capabilities
    client = get_enhanced_mcp_client()
    
    # Get available tools from all MCP servers
    mcp_tools = await client.get_tools()
    
    # Add think tool for research planning
    all_tools = mcp_tools + [think_tool]
    
    # Bind tools to the model
    enhanced_model_with_tools = enhanced_model.bind_tools(all_tools)
    
    # Get current messages and research context
    researcher_messages = state["researcher_messages"]
    
    # Create system message with enhanced capabilities
    system_message = SystemMessage(content=enhanced_research_agent_prompt_with_mcp.format(date=get_today_str()))
    messages = [system_message] + researcher_messages
    
    # Generate response with enhanced tools
    response = await enhanced_model_with_tools.ainvoke(messages)
    
    # Handle tool calls if present
    if response.tool_calls:
        # Execute tool calls using MCP client and tools
        tool_messages = []
        tools_by_name = {tool.name: tool for tool in all_tools}
        
        for tool_call in response.tool_calls:
            try:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                
                if tool_name in tools_by_name:
                    # Execute the tool
                    tool = tools_by_name[tool_name]
                    result = await tool.ainvoke(tool_args)
                    
                    tool_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                        name=tool_name
                    ))
                else:
                    # Handle unknown tool
                    error_msg = f"Unknown tool: {tool_name}"
                    tool_messages.append(ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call["id"],
                        name=tool_name
                    ))
                
            except Exception as e:
                # Handle tool execution errors gracefully
                error_msg = f"Tool execution error: {str(e)}"
                tool_messages.append(ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_call["id"],
                    name=tool_call.get("name", "unknown")
                ))
        
        return {
            "researcher_messages": [response] + tool_messages
        }
    
    # No tool calls, return response
    return {
        "researcher_messages": [response]
    }

async def enhanced_compress_research(state: ResearcherState) -> ResearcherOutputState:
    """Compress and synthesize research findings from enhanced sources."""
    
    # Get all messages for compression
    messages = state["researcher_messages"]
    
    # Create compression prompt with enhanced context
    system_message = SystemMessage(content=compress_research_system_prompt.format(date=get_today_str()))
    compression_message = HumanMessage(content=compress_research_human_message.format(
        research_topic="Enhanced research with Data Commons and local files"
    ))
    
    # Compress the research
    compression_model = init_chat_model(model="openai:gpt-4.1", max_tokens=32000)
    result = await compression_model.ainvoke([system_message, compression_message] + messages)
    
    return {
        "compressed_research": result.content
    }

# ===== ENHANCED WORKFLOW CONSTRUCTION =====

def should_continue_enhanced_research(state: ResearcherState) -> Literal["enhanced_researcher_agent", "enhanced_compress_research"]:
    """Determine if enhanced research should continue or be compressed."""
    
    messages = state["researcher_messages"]
    
    # Check if we have enough research (simple heuristic)
    if len(messages) >= 10:  # Arbitrary limit to prevent infinite loops
        return "enhanced_compress_research"
    
    # Check if the last message indicates research completion
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content') and last_message.content:
            content_lower = last_message.content.lower()
            if any(phrase in content_lower for phrase in [
                "research complete", "analysis finished", "investigation concluded",
                "no more information needed", "comprehensive overview provided"
            ]):
                return "enhanced_compress_research"
    
    # Continue research
    return "enhanced_researcher_agent"

# Build the enhanced research workflow
enhanced_researcher_builder = StateGraph(ResearcherState, output=ResearcherOutputState)

# Add enhanced nodes
enhanced_researcher_builder.add_node("enhanced_researcher_agent", enhanced_researcher_agent)
enhanced_researcher_builder.add_node("enhanced_compress_research", enhanced_compress_research)

# Set up enhanced workflow
enhanced_researcher_builder.add_edge(START, "enhanced_researcher_agent")
enhanced_researcher_builder.add_conditional_edges(
    "enhanced_researcher_agent",
    should_continue_enhanced_research,
    {
        "enhanced_researcher_agent": "enhanced_researcher_agent", 
        "enhanced_compress_research": "enhanced_compress_research"
    }
)
enhanced_researcher_builder.add_edge("enhanced_compress_research", END)

# Compile the enhanced agent
enhanced_agent_mcp = enhanced_researcher_builder.compile()

# Export enhanced agent for use in main application
agent_mcp_enhanced = enhanced_agent_mcp