#!/usr/bin/env python3
"""
Deep Research Agent - Interactive Demo

This script demonstrates the capabilities of the Deep Research Agent
with a series of example research queries across different modes.
"""

import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from deep_research_from_scratch.main import run_basic_research, run_mcp_research

console = Console()

DEMO_QUERIES = [
    {
        "title": "🚀 Technology Comparison",
        "query": "Compare React vs Vue.js for enterprise web development",
        "mode": "basic"
    },
    {
        "title": "🧬 Scientific Research",
        "query": "What are the latest breakthroughs in CRISPR gene editing?",
        "mode": "basic"  
    },
    {
        "title": "📊 Market Analysis", 
        "query": "Analyze the current state of the electric vehicle market",
        "mode": "basic"
    },
    {
        "title": "📁 Local File Analysis",
        "query": "What information do we have about coffee shops?",
        "mode": "mcp"
    }
]

async def run_demo():
    """Run interactive demo of the Deep Research Agent"""
    
    # Welcome header
    console.print(Panel.fit(
        "[bold blue]🔍 Deep Research Agent - Interactive Demo[/bold blue]\n"
        "[dim]Showcasing AI-powered research capabilities[/dim]",
        border_style="blue"
    ))
    
    console.print("\n[yellow]This demo will run several research queries to show the agent's capabilities.[/yellow]")
    console.print("[dim]Press Ctrl+C to skip to the next query or exit.\n[/dim]")
    
    for i, demo in enumerate(DEMO_QUERIES, 1):
        # Demo header
        console.print(f"\n[bold cyan]Demo {i}/{len(DEMO_QUERIES)}: {demo['title']}[/bold cyan]")
        console.print(f"[dim]Query: {demo['query']}[/dim]")
        console.print(f"[dim]Mode: {demo['mode'].upper()}[/dim]\n")
        
        # Ask user if they want to run this demo
        try:
            response = input("Press Enter to run this demo (or 's' to skip, 'q' to quit): ").strip().lower()
            
            if response == 'q':
                console.print("[yellow]Demo ended by user.[/yellow]")
                break
            elif response == 's':
                console.print("[dim]Skipped.[/dim]\n")
                continue
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted.[/yellow]")
            break
        
        # Run the research
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                
                if demo['mode'] == 'basic':
                    task = progress.add_task(f"Running basic research...", total=None)
                    result = await run_basic_research(demo['query'])
                elif demo['mode'] == 'mcp':
                    task = progress.add_task(f"Analyzing local files...", total=None)
                    result = await run_mcp_research(demo['query'])
            
            # Display results
            console.print("\n[bold green]✅ Research Complete![/bold green]\n")
            
            # Truncate very long results for demo
            if len(result) > 3000:
                result = result[:3000] + "\n\n[... truncated for demo ...]"
            
            console.print(Panel(
                Markdown(result),
                title="Research Results",
                border_style="green"
            ))
            
            # Wait before next demo
            console.print(f"\n[dim]Demo {i} complete. Moving to next demo...[/dim]")
            time.sleep(2)
            
        except KeyboardInterrupt:
            console.print(f"\n[yellow]Demo {i} skipped.[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[red]Error in demo {i}: {str(e)}[/red]")
            continue
    
    # Demo complete
    console.print(Panel.fit(
        "[bold green]🎉 Demo Complete![/bold green]\n"
        "[yellow]Ready to start your own research?[/yellow]\n"
        "\n"
        "[dim]Try these commands:[/dim]\n"
        "[cyan]• deep-research --interactive[/cyan]  (chat mode)\n"
        "[cyan]• streamlit run web_app.py[/cyan]     (web interface)\n"
        "[cyan]• deep-research -q 'your question'[/cyan]  (direct CLI)",
        border_style="green"
    ))

def main():
    """Main demo entry point"""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted. Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {str(e)}[/red]")

if __name__ == "__main__":
    main()