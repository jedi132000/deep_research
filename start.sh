#!/bin/bash

# Deep Research Agent - Enhanced Startup Script
# This script sets up and runs the Deep Research Agent with multiple interface options

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}🔍 Deep Research Agent - Startup Manager${NC}"
echo -e "${BLUE}===========================================${NC}"
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env template...${NC}"
    cat > .env << 'EOF'
# Deep Research Agent Configuration
# Copy this template and add your actual API keys

# Required for basic research
TAVILY_API_KEY=your_tavily_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: For enhanced MCP with Data Commons (NEW!)
DC_API_KEY=your_data_commons_api_key_here

# Optional for LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=deep-research

EOF
    echo -e "${GREEN}✅ Created .env template${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env with your actual API keys before proceeding${NC}"
    echo
    echo -e "${BLUE}📖 API Key Setup Guide:${NC}"
    echo "  • Tavily: https://app.tavily.com/"
    echo "  • OpenAI: https://platform.openai.com/api-keys"  
    echo "  • Anthropic: https://console.anthropic.com/"
    echo "  • Data Commons (NEW!): https://apikeys.datacommons.org/"
    echo "  • LangSmith (optional): https://smith.langchain.com/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Install the package
echo -e "${YELLOW}📦 Installing Deep Research Agent...${NC}"
pip install -e . > /dev/null 2>&1

echo
echo -e "${GREEN}✅ Setup complete!${NC}"
echo
echo -e "${BLUE}🎯 Choose an interface:${NC}"
echo "  ${PURPLE}1. web${NC}          - 🌐 Launch modern web interface (recommended)"
echo "  ${PURPLE}2. cli${NC}          - ⚡ Use command-line interface"
echo "  ${PURPLE}3. interactive${NC}  - 💬 Start interactive chat mode"
echo "  ${PURPLE}4. demo${NC}         - 🎬 Run interactive demonstration"
echo "  ${PURPLE}5. example${NC}      - 🧪 Run quick example script"
echo "  ${PURPLE}6. help${NC}         - 📖 Show usage help"
echo

# Run based on argument
case "${1:-help}" in
    "web")
        echo -e "${BLUE}🌐 Starting enhanced web interface...${NC}"
        pip install streamlit > /dev/null 2>&1
        echo -e "${GREEN}🚀 Web app starting at http://localhost:8501${NC}"
        streamlit run web_app.py --server.port=8501
        ;;
    "cli")
        echo -e "${BLUE}⚡ CLI Interface Ready${NC}"
        echo 
        .venv/bin/deep-research --help
        echo
        echo -e "${YELLOW}💡 Try: deep-research -q 'Compare AI models'${NC}"
        ;;
    "interactive")
        echo -e "${BLUE}� Starting interactive mode...${NC}"
        .venv/bin/deep-research --interactive
        ;;
    "demo")
        echo -e "${BLUE}🎬 Starting interactive demonstration...${NC}"
        python3 demo.py
        ;;
    "example")
        echo -e "${BLUE}🧪 Running example research...${NC}"
        .venv/bin/deep-research -q "What are the latest developments in quantum computing?" -m basic
        ;;
    "help"|*)
        echo -e "${BLUE}📖 Deep Research Agent Usage:${NC}"
        echo
        echo -e "${YELLOW}Quick Start:${NC}"
        echo "  ./start.sh web          # Launch web interface"
        echo "  ./start.sh demo         # Interactive demonstration"
        echo "  ./start.sh interactive  # Start chat mode"
        echo 
        echo -e "${YELLOW}Research Commands:${NC}"
        echo "  deep-research -q 'your question'                    # Basic research"
        echo "  deep-research -m mcp -q 'analyze local files'       # Local file research"
        echo "  deep-research -m full -q 'comprehensive analysis'   # Multi-agent research"
        echo
        echo -e "${YELLOW}Development:${NC}"
        echo "  jupyter notebook        # Open tutorial notebooks"
        echo "  pytest                  # Run tests"
        echo
        echo -e "${GREEN}✨ Tip: Start with './start.sh demo' to see what's possible!${NC}"
        ;;
esac
        python example.py
        ;;
    "interactive")
        echo "🚀 Starting interactive mode..."
        .venv/bin/deep-research --interactive
        ;;
    "help"|*)
        echo "Usage: ./start.sh [cli|web|example|interactive]"
        ;;
esac