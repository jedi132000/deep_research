"""
Deep Research Agent - Main Application Entry Point

This module provides the main CLI interface for running the deep research agent.
Supports multiple research modes including basic research, MCP-enabled research,
and full multi-agent research workflows.
"""

import asyncio
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage

# Import research agents
from .research_agent_scope import scope_research

console = Console()

async def run_scoping_research(query: str) -> str:
    """Run scoping research to clarify user intent and generate research brief"""
    try:
        from .state_scope import AgentInputState
        
        # Create initial state with user query
        initial_state = AgentInputState(
            messages=[HumanMessage(content=query)]
        )
        
        # Run the scoping workflow
        result = await scope_research.ainvoke(initial_state)
        
        # The scoping workflow puts the final message (clarification question or verification) 
        # in the messages list. The last message is the AI's response.
        messages = result.get("messages", [])
        if not messages:
            return "**Scoping Error**\\n\\nNo response received from scoping agent."
        
        # Get the last AI message (the scoping agent's response)
        last_message = messages[-1]
        ai_response = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Check if this contains a research brief (successful scoping)
        if result.get("research_brief"):
            formatted_brief = f"""## 📋 Research Brief Generated

{result['research_brief']}

---
✅ **Ready to Research**: This research brief will guide the investigation. You can now proceed with your preferred research mode for detailed results."""
            return formatted_brief
        
        # If no research brief, this means clarification was needed
        # Check if the AI response looks like a clarifying question (contains question marks or specific keywords)
        if any(indicator in ai_response.lower() for indicator in ['?', 'clarify', 'please provide', 'could you', 'what specific', 'more details']):
            formatted_response = f"""## 🤔 Clarification Needed

{ai_response}

---
💡 **Next Steps**: Please provide more specific details about what you'd like to research, and I'll help you get better, more focused results.

**Helpful details to include:**
- Specific time period or geographic focus
- Particular aspects you're most interested in  
- Intended use case or audience for the research
- Any constraints or requirements"""
            return formatted_response
        
        # Otherwise, it's a verification that we can proceed
        formatted_complete = f"""## ✅ Scoping Complete

{ai_response}

---
🚀 **Ready to Proceed**: Your query is well-scoped and ready for research. Continue with your selected research mode for comprehensive results."""
        return formatted_complete
        
    except Exception as e:
        # Handle various types of errors gracefully
        error_msg = str(e).lower()
        if "authentication" in error_msg or "api_key" in error_msg:
            return f"**Configuration Issue**\\n\\nThe scoping feature requires proper API configuration. Please check your .env file contains valid API keys.\\n\\n*Error: {str(e)}*"
        elif "model" in error_msg:
            return f"**Model Issue**\\n\\nThere was an issue with the AI model. Please try again or use a different research mode.\\n\\n*Error: {str(e)}*"
        else:
            return f"**Scoping Error**\\n\\nUnable to process the scoping request: {str(e)}\\n\\n*Please try rephrasing your query or use a different research mode.*"

async def run_basic_research(query: str) -> str:
    """Run basic research agent without MCP"""
    from .research_agent import researcher_agent
    
    console.print(Panel("[bold blue]Running Basic Research Agent[/bold blue]", expand=False))
    
    result = await researcher_agent.ainvoke({"researcher_messages": [HumanMessage(content=query)]})
    return result.get('compressed_research', 'No research results found')

async def run_mcp_research(query: str) -> str:
    """Run MCP-enabled research agent with filesystem access"""
    try:
        from .research_agent_mcp import agent_mcp
        
        console.print(Panel("[bold green]Running MCP Research Agent[/bold green]", expand=False))
        
        result = await agent_mcp.ainvoke({"researcher_messages": [HumanMessage(content=query)]})
        return result.get('compressed_research', 'No research results found')
    except ImportError as e:
        console.print(f"[red]MCP dependencies not available: {e}[/red]")
        return "MCP research not available. Please ensure Node.js and MCP packages are installed."

async def run_enhanced_mcp_research(query: str) -> str:
    """Run enhanced MCP research agent with Data Commons + filesystem access"""
    try:
        from .research_agent_mcp_enhanced import agent_mcp_enhanced
        
        console.print(Panel("[bold blue]Running Enhanced MCP Research Agent with Data Commons[/bold blue]", expand=False))
        
        result = await agent_mcp_enhanced.ainvoke({"researcher_messages": [HumanMessage(content=query)]})
        return result.get('compressed_research', 'No research results found')
    except ImportError as e:
        console.print(f"[red]Enhanced MCP dependencies not available: {e}[/red]")
        return "Enhanced MCP research not available. Please ensure Node.js, MCP packages, and Data Commons API key are configured."

async def run_full_research(query: str) -> str:
    """Run full multi-agent research system with scoping and final report"""
    from .research_agent_full import deep_researcher_builder
    from langgraph.checkpoint.memory import InMemorySaver
    
    console.print(Panel("[bold yellow]Running Full Multi-Agent Research System[/bold yellow]", expand=False))
    
    checkpointer = InMemorySaver()
    full_agent = deep_researcher_builder.compile(checkpointer=checkpointer)
    
    # Configure with higher recursion limit for complex workflows
    config = {"configurable": {"thread_id": "main", "recursion_limit": 50}}
    
    result = await full_agent.ainvoke(
        {"messages": [HumanMessage(content=query)]}, 
        config=config
    )
    
    return result.get('final_report', 'No final report generated')

# ===== SCOPED RESEARCH METHODS =====
# These methods automatically run scoping first, then proceed with research

async def run_scoped_basic_research(query: str) -> str:
    """Run basic research with automatic scoping first"""
    console.print(Panel("[bold cyan]Running Scoped Basic Research[/bold cyan]\n[dim]Step 1: Query Clarification & Scoping[/dim]", expand=False))
    
    # Step 1: Run scoping to clarify the query
    scoping_result = await run_scoping_research(query)
    
    # Check if clarification is needed
    if "Clarification Needed" in scoping_result:
        return f"**Scoping Phase**\n\n{scoping_result}\n\n*Please provide the requested clarification, then run the research again.*"
    
    # Step 2: Extract research brief or use original query
    research_query = query
    if "Research Brief Generated" in scoping_result:
        # Extract the research brief from the scoping result
        import re
        brief_match = re.search(r'\*\*Research Brief Generated\*\*\n\n(.*?)\n\n\*', scoping_result, re.DOTALL)
        if brief_match:
            research_query = brief_match.group(1).strip()
    
    console.print(Panel("[dim]Step 2: Conducting Research[/dim]", expand=False))
    
    # Step 3: Run the actual research
    research_result = await run_basic_research(research_query)
    
    return f"**Research Complete**\n\n{research_result}"

async def run_scoped_mcp_research(query: str) -> str:
    """Run MCP research with automatic scoping first"""
    console.print(Panel("[bold cyan]Running Scoped MCP Research[/bold cyan]\n[dim]Step 1: Query Clarification & Scoping[/dim]", expand=False))
    
    # Step 1: Run scoping to clarify the query
    scoping_result = await run_scoping_research(query)
    
    # Check if clarification is needed
    if "Clarification Needed" in scoping_result:
        return f"**Scoping Phase**\n\n{scoping_result}\n\n*Please provide the requested clarification, then run the research again.*"
    
    # Step 2: Extract research brief or use original query
    research_query = query
    if "Research Brief Generated" in scoping_result:
        # Extract the research brief from the scoping result
        import re
        brief_match = re.search(r'\*\*Research Brief Generated\*\*\n\n(.*?)\n\n\*', scoping_result, re.DOTALL)
        if brief_match:
            research_query = brief_match.group(1).strip()
    
    console.print(Panel("[dim]Step 2: Conducting MCP Research[/dim]", expand=False))
    
    # Step 3: Run the actual research
    research_result = await run_mcp_research(research_query)
    
    return f"**Research Complete**\n\n{research_result}"

async def run_scoped_enhanced_mcp_research(query: str) -> str:
    """Run enhanced MCP research with automatic scoping first"""
    console.print(Panel("[bold cyan]Running Scoped Enhanced MCP Research[/bold cyan]\n[dim]Step 1: Query Clarification & Scoping[/dim]", expand=False))
    
    # Step 1: Run scoping to clarify the query
    scoping_result = await run_scoping_research(query)
    
    # Check if clarification is needed
    if "Clarification Needed" in scoping_result:
        return f"**Scoping Phase**\n\n{scoping_result}\n\n*Please provide the requested clarification, then run the research again.*"
    
    # Step 2: Extract research brief or use original query
    research_query = query
    if "Research Brief Generated" in scoping_result:
        # Extract the research brief from the scoping result
        import re
        brief_match = re.search(r'\*\*Research Brief Generated\*\*\n\n(.*?)\n\n\*', scoping_result, re.DOTALL)
        if brief_match:
            research_query = brief_match.group(1).strip()
    
    console.print(Panel("[dim]Step 2: Conducting Enhanced MCP Research[/dim]", expand=False))
    
    # Step 3: Run the actual research
    research_result = await run_enhanced_mcp_research(research_query)
    
    return f"**Research Complete**\n\n{research_result}"

async def run_scoped_full_research(query: str) -> str:
    """Run full research with automatic scoping first"""
    console.print(Panel("[bold cyan]Running Scoped Full Research[/bold cyan]\n[dim]Step 1: Query Clarification & Scoping[/dim]", expand=False))
    
    # Step 1: Run scoping to clarify the query
    scoping_result = await run_scoping_research(query)
    
    # Check if clarification is needed
    if "Clarification Needed" in scoping_result:
        return f"**Scoping Phase**\n\n{scoping_result}\n\n*Please provide the requested clarification, then run the research again.*"
    
    # Step 2: Extract research brief or use original query
    research_query = query
    if "Research Brief Generated" in scoping_result:
        # Extract the research brief from the scoping result
        import re
        brief_match = re.search(r'\*\*Research Brief Generated\*\*\n\n(.*?)\n\n\*', scoping_result, re.DOTALL)
        if brief_match:
            research_query = brief_match.group(1).strip()
    
    console.print(Panel("[dim]Step 2: Conducting Full Multi-Agent Research[/dim]", expand=False))
    
    # Step 3: Run the actual research
    research_result = await run_full_research(research_query)
    
    return f"**Research Complete**\n\n{research_result}"

async def interactive_mode():
    """Run interactive research session"""
    console.print(Panel(
        "[bold cyan]Deep Research Agent - Interactive Mode[/bold cyan]\n\n"
        "Available commands:\n"
        "• [yellow]/scope <query>[/yellow] - Clarify research intent and generate brief\n\n"
        "[bold]Research Methods:[/bold]\n"
        "• [yellow]/basic <query>[/yellow] - Basic web research\n"
        "• [yellow]/mcp <query>[/yellow] - Research with local files\n"
        "• [yellow]/enhanced <query>[/yellow] - Enhanced research with Data Commons\n"
        "• [yellow]/full <query>[/yellow] - Comprehensive multi-agent research\n\n"
        "[bold]Scoped Research Methods (with automatic query clarification):[/bold]\n"
        "• [yellow]/scoped-basic <query>[/yellow] - Scoped basic research\n"
        "• [yellow]/scoped-mcp <query>[/yellow] - Scoped MCP research\n"
        "• [yellow]/scoped-enhanced <query>[/yellow] - Scoped enhanced research\n"
        "• [yellow]/scoped-full <query>[/yellow] - Scoped full research\n\n"
        "• [yellow]/quit[/yellow] - Exit interactive mode\n\n"
        "[dim]Or just type your query for basic research[/dim]",
        title="Welcome to Deep Research",
        border_style="cyan"
    ))
    
    while True:
        try:
            user_input = console.input("[bold]>> [/bold]").strip()
            
            if not user_input:
                continue
                
            if user_input == "/quit":
                console.print("[green]Goodbye![/green]")
                break
                
            if user_input.startswith("/scope "):
                query = user_input[7:]
                result = await run_scoping_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/basic "):
                query = user_input[7:]
                result = await run_basic_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/mcp "):
                query = user_input[5:]
                result = await run_scoped_mcp_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/enhanced "):
                query = user_input[10:]
                result = await run_scoped_enhanced_mcp_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/full "):
                query = user_input[6:]
                result = await run_scoped_full_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/scoped-basic "):
                query = user_input[14:]
                result = await run_scoped_basic_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/scoped-mcp "):
                query = user_input[12:]
                result = await run_scoped_mcp_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/scoped-enhanced "):
                query = user_input[17:]
                result = await run_scoped_enhanced_mcp_research(query)
                console.print(Markdown(result))
                
            elif user_input.startswith("/scoped-full "):
                query = user_input[13:]
                result = await run_scoped_full_research(query)
                console.print(Markdown(result))
                
            else:
                # Default to basic research (no scoping)
                result = await run_basic_research(user_input)
                console.print(Markdown(result))
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use /quit to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Deep Research Agent - AI-powered research assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m deep_research_from_scratch.main --query "Compare AI models"
  python -m deep_research_from_scratch.main --mode mcp --query "Analyze local documents"
  python -m deep_research_from_scratch.main --interactive
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Research query to execute"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["scope", "basic", "mcp", "enhanced", "full", "scoped-basic", "scoped-mcp", "scoped-enhanced", "scoped-full"],
        default="basic",
        help="Research mode to use (default: basic). Scoped modes automatically run query clarification first."
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    async def run():
        if args.interactive:
            await interactive_mode()
        elif args.query:
            result = None  # Initialize result variable
            
            if args.mode == "scope":
                result = await run_scoping_research(args.query)
            elif args.mode == "basic":
                result = await run_basic_research(args.query)
            elif args.mode == "mcp":
                result = await run_scoped_mcp_research(args.query)
            elif args.mode == "enhanced":
                result = await run_scoped_enhanced_mcp_research(args.query)
            elif args.mode == "full":
                result = await run_scoped_full_research(args.query)
            elif args.mode == "scoped-basic":
                result = await run_scoped_basic_research(args.query)
            elif args.mode == "scoped-mcp":
                result = await run_scoped_mcp_research(args.query)
            elif args.mode == "scoped-enhanced":
                result = await run_scoped_enhanced_mcp_research(args.query)
            elif args.mode == "scoped-full":
                result = await run_scoped_full_research(args.query)
            else:
                result = "**Error**: Unknown research mode specified."
            
            if result:
                console.print(Markdown(result))
        else:
            parser.print_help()
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())