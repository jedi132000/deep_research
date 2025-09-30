# 🧱 Deep Research Agent

> **Accelerate your insights with multi-mode AI research**

An AI-powered research assistant that conducts comprehensive research using multiple modes and specialized agents. Built with LangGraph and designed for both researchers and developers who need deep, accurate, and well-sourced information.

Deep research has broken out as one of the most popular agent applications. [OpenAI](https://openai.com/index/introducing-deep-research/), [Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), and [Google](https://gemini.google/overview/deep-research/?hl=en) all have deep research products that produce comprehensive reports using [various sources](https://www.anthropic.com/news/research) of context. There are also many [open](https://huggingface.co/blog/open-deep-research) [source](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) implementations.

This repository implements a complete deep research system built from scratch with multiple research modes, agent coordination, and professional interfaces.

![Deep Research Agent Overview](https://github.com/user-attachments/assets/b71727bd-0094-40c4-af5e-87cdb02123b4)

---

## ✨ Features

### 🔍 **Multiple Research Modes**
- **🚀 Basic Research**: Lightning-fast web search with advanced algorithms
- **📁 MCP Research**: Intelligent local file analysis using Model Context Protocol  
- **🌍 Enhanced MCP Research**: **NEW!** Local files + Google Data Commons statistical datasets
- **🧠 Full Multi-Agent**: Comprehensive workflow with specialized agent orchestration
- **💬 Interactive Mode**: Chat-based interface for iterative research sessions

### 🎯 **Professional Interfaces**
- **🌐 Enhanced Web UI**: Modern, responsive Streamlit interface with research history
- **⚡ CLI Tool**: Powerful command-line interface for automation and scripting
- **📚 Python API**: Programmatic access for integration into other systems

### 🛠 **Advanced Capabilities**
- **Multi-source Research**: Combines web search, local files, and structured analysis
- **Citation Management**: Automatic source tracking and formatted references
- **Research History**: Persistent session memory and query management
- **Export Options**: Markdown downloads and clipboard integration

---

## Installation

### Quick Install

```bash
pip install -e .
```

### With Optional Dependencies

```bash
# For web interface
pip install -e ".[web]"

# For enhanced MCP with Data Commons (optional)
pip install -e ".[enhanced]"

# Install everything
pip install -e ".[all]"
```

### Prerequisites

#### **For Enhanced MCP Research (NEW!)**

Get access to Google's Data Commons - a vast repository of public statistical data:

```bash
# 1. Get a free Data Commons API key
# Visit: https://apikeys.datacommons.org/
# Request access for api.datacommons.org domain

# 2. Add to your .env file
echo "DC_API_KEY=your_data_commons_api_key" >> .env

# 3. Install enhanced dependencies
pip install -e ".[enhanced]"
```

#### **For MCP Research**

For MCP research mode, you need Node.js installed:

```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Windows
# Download from https://nodejs.org/
```

- **Node.js and npx** (required for MCP server in notebook 3):
```bash
# Install Node.js (includes npx)
# On macOS with Homebrew:
brew install node

# On Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation:
node --version
npx --version
```

- Ensure you're using Python 3.11 or later.
- This version is required for optimal compatibility with LangGraph.
```bash
python3 --version
```
- [uv](https://docs.astral.sh/uv/) package manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Update PATH to use the new uv version
export PATH="/Users/$USER/.local/bin:$PATH"
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/langchain-ai/deep_research_from_scratch
cd deep_research_from_scratch
```

2. Install the package and dependencies (this automatically creates and manages the virtual environment):
```bash
uv sync
```

3. Create a `.env` file in the project root with your API keys:
```bash
# Create .env file
touch .env
```

Add your API keys to the `.env` file:
```env
# Required for research agents with external search
TAVILY_API_KEY=your_tavily_api_key_here

# Required for model usage
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: For evaluation and tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deep_research_from_scratch
```

4. Run notebooks or code using uv:
```bash
# Run Jupyter notebooks directly
uv run jupyter notebook

# Or activate the virtual environment if preferred
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
jupyter notebook
```

---

## 🚀 Usage Guide

### 🌐 **Web Interface** (Recommended)

Launch the enhanced web interface for the best user experience:

```bash
# Start the web application
source .venv/bin/activate
streamlit run web_app.py

# Or with uv
uv run streamlit run web_app.py
```

**Features:**
- **🎨 Modern UI**: Gradient header, card-based design, and responsive layout
- **📊 Research Modes**: Visual radio button selection with detailed descriptions
- **📚 Research History**: Collapsible sidebar with recent queries and one-click repeat
- **⬇️ Export Options**: Download results as Markdown or copy to clipboard  
- **💡 Pro Tips**: Built-in guidance for better research queries
- **♿ Accessibility**: Keyboard shortcuts, proper labeling, and high contrast

**Access**: Open http://localhost:8501 in your browser

### ⚡ **Command Line Interface**

For automation, scripting, and power users:

```bash
# Basic research (fastest)
deep-research --query "Compare quantum computing vs classical computing performance"

# MCP research (local files)  
deep-research --mode mcp --query "Summarize my project documentation"

# Enhanced MCP research (local files + Data Commons statistics)
deep-research --mode enhanced --query "Compare GDP growth rates with local economic analysis"

# Full multi-agent research (most comprehensive)
deep-research --mode full --query "Analyze the competitive landscape of AI startups"

# Interactive mode (chat-based)
deep-research --interactive

# Get help
deep-research --help
```

**Interactive Commands:**
- `/basic <query>` - Run fast basic research (no scoping)
- `/mcp <query>` - Run MCP research with local files (includes scoping)
- `/enhanced <query>` - **NEW!** Run enhanced MCP with Data Commons + local files (includes scoping)
- `/full <query>` - Run comprehensive multi-agent research (includes scoping)
- `/scoped-basic <query>` - Run basic research with scoping step
- `/quit` - Exit interactive mode

### 🐍 **Python API**

For programmatic integration:

```python
import asyncio
from deep_research_from_scratch.main import run_basic_research

# Basic research
result = asyncio.run(run_basic_research("Your research question"))
print(result)

# With custom configuration
from deep_research_from_scratch.research_agent import researcher_agent
from langchain_core.messages import HumanMessage

response = await researcher_agent.ainvoke({
    "researcher_messages": [HumanMessage(content="Your query")]
})
```

### 📝 **Quick Start Examples**

```bash
# Technology comparison
deep-research -q "Compare React vs Vue.js for enterprise applications"

# Market research with statistics
deep-research -m enhanced -q "Analyze unemployment trends in BRICS nations using statistical data"

# Academic research
deep-research -q "Summarize recent breakthroughs in CRISPR gene editing"

# Local document analysis
deep-research -m mcp -q "What are the key findings in my research notes?"

# Statistical analysis with Data Commons
deep-research -m enhanced -q "Compare healthcare outcomes across US states"

# Economic data analysis
deep-research -m enhanced -q "Generate a report on income vs education levels globally"
```

---

## Background 

Research is an open‑ended task; the best strategy to answer a user request can’t be easily known in advance. Requests can require different research strategies and varying levels of search depth. Consider this request. 

[Agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/#agent) are well suited to research because they can flexibly apply different strategies, using intermediate results to guide their exploration. Open deep research uses an agent to conduct research as part of a three step process:

1. **Scope** – clarify research scope
2. **Research** – perform research
3. **Write** – produce the final report

## 📝 Organization 

This repo contains 5 tutorial notebooks that build a deep research system from scratch:

### 📚 Tutorial Notebooks

#### 1. User Clarification and Brief Generation (`notebooks/1_scoping.ipynb`)
**Purpose**: Clarify research scope and transform user input into structured research briefs

**Key Concepts**:
- **User Clarification**: Determines if additional context is needed from the user using structured output
- **Brief Generation**: Transforms conversations into detailed research questions
- **LangGraph Commands**: Using Command system for flow control and state updates
- **Structured Output**: Pydantic schemas for reliable decision making

**Implementation Highlights**:
- Two-step workflow: clarification → brief generation
- Structured output models (`ClarifyWithUser`, `ResearchQuestion`) to prevent hallucination
- Conditional routing based on clarification needs
- Date-aware prompts for context-sensitive research

**What You'll Learn**: State management, structured output patterns, conditional routing

---

#### 2. Research Agent with Custom Tools (`notebooks/2_research_agent.ipynb`)
**Purpose**: Build an iterative research agent using external search tools

**Key Concepts**:
- **Agent Architecture**: LLM decision node + tool execution node pattern
- **Sequential Tool Execution**: Reliable synchronous tool execution
- **Search Integration**: Tavily search with content summarization
- **Tool Execution**: ReAct-style agent loop with tool calling

**Implementation Highlights**:
- Synchronous tool execution for reliability and simplicity
- Content summarization to compress search results
- Iterative research loop with conditional routing
- Rich prompt engineering for comprehensive research

**What You'll Learn**: Agent patterns, tool integration, search optimization, research workflow design

---

#### 3. Research Agent with MCP (`notebooks/3_research_agent_mcp.ipynb`)
**Purpose**: Integrate Model Context Protocol (MCP) servers as research tools

**Key Concepts**:
- **Model Context Protocol**: Standardized protocol for AI tool access
- **MCP Architecture**: Client-server communication via stdio/HTTP
- **LangChain MCP Adapters**: Seamless integration of MCP servers as LangChain tools
- **Local vs Remote MCP**: Understanding transport mechanisms

**Implementation Highlights**:
- `MultiServerMCPClient` for managing MCP servers
- Configuration-driven server setup (filesystem example)
- Rich formatting for tool output display
- Async tool execution required by MCP protocol (no nested event loops needed)

**What You'll Learn**: MCP integration, client-server architecture, protocol-based tool access

---

#### 4. Research Supervisor (`notebooks/4_research_supervisor.ipynb`)
**Purpose**: Multi-agent coordination for complex research tasks

**Key Concepts**:
- **Supervisor Pattern**: Coordination agent + worker agents
- **Parallel Research**: Concurrent research agents for independent topics using parallel tool calls
- **Research Delegation**: Structured tools for task assignment
- **Context Isolation**: Separate context windows for different research topics

**Implementation Highlights**:
- Two-node supervisor pattern (`supervisor` + `supervisor_tools`)
- Parallel research execution using `asyncio.gather()` for true concurrency
- Structured tools (`ConductResearch`, `ResearchComplete`) for delegation
- Enhanced prompts with parallel research instructions
- Comprehensive documentation of research aggregation patterns

**What You'll Learn**: Multi-agent patterns, parallel processing, research coordination, async orchestration

---

#### 5. Full Multi-Agent Research System (`notebooks/5_full_agent.ipynb`)
**Purpose**: Complete end-to-end research system integrating all components

**Key Concepts**:
- **Three-Phase Architecture**: Scope → Research → Write
- **System Integration**: Combining scoping, multi-agent research, and report generation
- **State Management**: Complex state flow across subgraphs
- **End-to-End Workflow**: From user input to final research report

**Implementation Highlights**:
- Complete workflow integration with proper state transitions
- Supervisor and researcher subgraphs with output schemas
- Final report generation with research synthesis
- Thread-based conversation management for clarification

**What You'll Learn**: System architecture, subgraph composition, end-to-end workflows

---

### 🎯 Key Learning Outcomes

- **Structured Output**: Using Pydantic schemas for reliable AI decision making
- **Async Orchestration**: Strategic use of async patterns for parallel coordination vs synchronous simplicity
- **Agent Patterns**: ReAct loops, supervisor patterns, multi-agent coordination
- **Search Integration**: External APIs, MCP servers, content processing
- **Workflow Design**: LangGraph patterns for complex multi-step processes
- **State Management**: Complex state flows across subgraphs and nodes
- **Protocol Integration**: MCP servers and tool ecosystems

Each notebook builds on the previous concepts, culminating in a production-ready deep research system that can handle complex, multi-faceted research queries with intelligent scoping and coordinated execution. 
