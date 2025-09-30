#!/usr/bin/env python3
"""
Deep Research Web Interface

Enhanced Streamlit web interface for the Deep Research Agent with improved UI/UX
"""

import streamlit as st
import asyncio
import time
from typing import Optional

# Import research functions (Basic Research is direct, others use scoping)
from src.deep_research_from_scratch.main import (
    run_basic_research,
    run_scoped_mcp_research as run_mcp_research,
    run_scoped_enhanced_mcp_research as run_enhanced_mcp_research,
    run_scoped_full_research as run_full_research
)

# Import cost tracking, virtual assistant, and clarification chatbot
from src.deep_research_from_scratch.cost_tracker import cost_tracker
from src.deep_research_from_scratch.virtual_assistant import virtual_assistant
from src.deep_research_from_scratch.clarification_chatbot import clarification_chatbot

# Configure Streamlit
st.set_page_config(
    page_title="Deep Research from Scratch",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Mode cards styling */
    .mode-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .mode-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .mode-card.selected {
        border-color: #667eea;
        background: linear-gradient(145deg, #f8f9ff, #ffffff);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .mode-title {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .mode-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .mode-features {
        background: #f8f9fa;
        border-radius: 5px;
        padding: 0.75rem;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        color: #555;
    }
    
    /* Progress indicators */
    .progress-container {
        background: linear-gradient(135deg, #f8f9ff, #ffffff);
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .progress-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .progress-title {
        color: #4f46e5;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .research-avatar {
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .status-message {
        background: #e0f2fe;
        border-left: 4px solid #0288d1;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .step-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
        .step-completed {\n        background: #e8f5e8;\n        border-left: 3px solid #4caf50;\n        /* Remove animations for completed state */\n    }\n    \n    .step-current {\n        background: #fff3e0;\n        border-left: 3px solid #ff9800;\n        animation: pulse 1.5s infinite;\n    }\n    \n    .step-pending {\n        background: #f5f5f5;\n        border-left: 3px solid #ccc;\n        opacity: 0.7;\n    }\n    \n    /* Stop all animations when research is complete */\n    .research-complete .research-avatar,\n    .research-complete .progress-container::before,\n    .research-complete .step-current {\n        animation: none !important;\n    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Results styling */
    .results-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Input styling */
    .stTextArea textarea {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1rem;
        padding: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header with enhanced branding
st.markdown("""
<div class="main-header">
    <h1>🔬 Deep Research from Scratch</h1>
    <p>Advanced AI-Powered Research Platform with Multi-Source Data Integration</p>
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
        ✨ Local Files • 🌐 Web Search • 📊 Statistical Data • 🤖 Multi-Agent Analysis
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar for mode selection
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; color: white; margin-bottom: 1.5rem;'><h2 style='margin: 0; font-size: 1.5rem;'>🎯 Research Configuration</h2></div>", unsafe_allow_html=True)
    
    st.markdown("### Select Research Mode")
    st.markdown("Choose the approach that best fits your research needs:")
    
    mode = st.radio(
        "Research Modes:",
        options=[
            "Basic Research",
            "MCP Research", 
            "Enhanced MCP Research",
            "Full Research"
        ],
        index=2,  # Default to Enhanced MCP Research
        help="Each mode offers different capabilities and data sources"
    )
    
    st.markdown("---")
    
    # Enhanced mode descriptions with visual cards
    mode_info = {
        "Basic Research": {
            "icon": "🔍",
            "title": "Basic Research",
            "description": "Fast, direct web research - no scoping step. Perfect for quick queries and testing connectivity.",
            "features": ["🌐 Web search via Tavily", "⚡ Lightning fast", "🎯 Direct execution", "💰 Low token usage"]
        },
        "MCP Research": {
            "icon": "📁",
            "title": "MCP Research", 
            "description": "Local document analysis through Model Context Protocol for file-based research.",
            "features": ["📁 Local file access", "📄 Document analysis", "📝 Content extraction", "🔒 Privacy focused"]
        },
        "Enhanced MCP Research": {
            "icon": "🌍",
            "title": "Enhanced MCP Research",
            "description": "Combines local files with Google Data Commons for comprehensive statistical analysis.",
            "features": ["📁 Local documents", "📊 Statistical data", "🌐 Public datasets", "🔬 Multi-source analysis"]
        },
        "Full Research": {
            "icon": "⚡",
            "title": "Full Research",
            "description": "Comprehensive research combining web search, document analysis, and advanced synthesis.",
            "features": ["🌐 Web search", "📄 Document analysis", "🧠 Advanced synthesis", "📋 Detailed reports"]
        }
    }
    
    current_mode = mode_info[mode]
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #f8f9ff, #ffffff);
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{current_mode['icon']} <strong>{current_mode['title']}</strong></div>
        <div style="color: #2d3748; margin-bottom: 1rem; line-height: 1.5;">{current_mode['description']}</div>
        <div style="background: #f0f4ff; padding: 1rem; border-radius: 5px; font-size: 0.9rem; color: #1a202c;">
            <strong>Key Features:</strong><br>
            {'<br>'.join(current_mode['features'])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

# Cost Estimation Section
st.markdown("### 💰 Cost Estimation")

# Get cost estimate for selected mode
if 'query_preview' in locals() or True:  # Always show estimates
    try:
        query_length = len(st.session_state.get('query_input', '')) if 'query_input' in st.session_state else 100
        cost_estimate = cost_tracker.estimate_research_cost(mode, query_length)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Estimated Cost",
                value=f"${cost_estimate['estimated_total_usd']:.4f}",
                help="Estimated total cost in USD for this research query"
            )
        
        with col2:
            st.metric(
                label="Input Tokens",
                value=f"{cost_estimate['estimated_input_tokens']:,}",
                help="Estimated tokens sent to AI models"
            )
        
        with col3:
            st.metric(
                label="Output Tokens", 
                value=f"{cost_estimate['estimated_output_tokens']:,}",
                help="Estimated tokens generated by AI models"
            )
        
        with col4:
            st.metric(
                label="Search Calls",
                value=cost_estimate['estimated_searches'],
                help="Estimated number of web searches"
            )
        
        # Cost breakdown
        with st.expander("📊 Cost Breakdown", expanded=False):
            st.write(f"**Model Costs**: ${cost_estimate['model_cost_usd']:.4f}")
            st.write(f"**Search Costs**: ${cost_estimate['search_cost_usd']:.4f}")
            st.write("**Note**: Estimates based on typical usage patterns. Actual costs may vary.")
            
    except Exception as e:
        st.error(f"Could not calculate cost estimate: {str(e)}")

# Daily usage summary in sidebar
if st.sidebar.checkbox("📈 Show Daily Usage", value=False):
    try:
        daily_summary = cost_tracker.get_daily_summary()
        if daily_summary['total_sessions'] > 0:
            st.sidebar.markdown("### 📊 Today's Usage")
            st.sidebar.metric("Total Cost", f"${daily_summary['total_cost_usd']:.4f}")
            st.sidebar.metric("Sessions", daily_summary['total_sessions'])
            st.sidebar.metric("Avg Cost/Session", f"${daily_summary['average_cost_per_session']:.4f}")
        else:
            st.sidebar.info("No usage data for today")
    except Exception as e:
        st.sidebar.error(f"Usage data unavailable: {str(e)}")

# Research tips
st.markdown("### 💡 Research Tips")
st.info("💡 **Pro Tip**: Start with Basic Research for cost-effective queries, then use Enhanced modes for comprehensive analysis.")

# Add quota warning for users
if mode in ["Enhanced MCP Research", "Full Research"]:
    st.warning(f"⚠️ **Higher Cost**: {mode} uses more API calls and will cost more than Basic Research.")
elif mode == "Basic Research":
    st.success("💰 **Cost Optimized**: Basic Research uses fast, cost-effective models for quick results.")

if mode == "Enhanced MCP Research":
    st.info("🌟 **Enhanced Mode**: Access to local files + Data Commons statistical data!")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #2d3748; font-size: 0.8rem;'>Powered by LangGraph & OpenAI</div>", unsafe_allow_html=True)

# Initialize session state for input clearing
if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False
if 'submitted_query' not in st.session_state:
    st.session_state.submitted_query = ""
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Debug information
st.sidebar.markdown("### 🐛 Debug Info")
st.sidebar.write(f"clear_input: {st.session_state.clear_input}")
st.sidebar.write(f"submitted_query: '{st.session_state.submitted_query}'")
st.sidebar.write(f"input_key: {st.session_state.input_key}")
st.sidebar.write(f"processing: {st.session_state.get('processing', False)}")

# Show all session state for complete debugging
st.sidebar.markdown("#### 📋 Full Session State")
debug_state = {k: str(v)[:100] for k, v in st.session_state.items() if isinstance(k, str) and not k.startswith('FormSubmitter')}
st.sidebar.json(debug_state)

# Add debugging for current text area value
st.sidebar.markdown("#### 🔍 Text Area Debug")
current_key = f"query_input_{st.session_state.input_key}"
st.sidebar.write(f"Current text area key: {current_key}")
if current_key in st.session_state:
    st.sidebar.write(f"Current text area value: '{st.session_state[current_key]}'")
else:
    st.sidebar.write("Text area not in session state yet")

# Enhanced main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📝 Research Query")
    
    # Check if this is an advanced mode that needs clarification chatbot
    advanced_modes = ["MCP Research", "Enhanced MCP Research", "Full Research"]
    is_advanced_mode = mode in advanced_modes
    
    # Conversational Clarification Chatbot - Only for advanced modes
    if is_advanced_mode:
        st.markdown("#### 💬 Advanced Research Clarification Assistant")
        st.info("🎯 **Advanced Mode Active**: The clarification chat will help optimize your complex research queries for better results.")
        
        # Initialize chatbot session state
        if 'chatbot_active' not in st.session_state:
            st.session_state.chatbot_active = True  # Auto-active for advanced modes
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'chat_timestamp' not in st.session_state:
            st.session_state.chat_timestamp = 0
        
        # Auto-activate for advanced modes
        if is_advanced_mode and not st.session_state.chatbot_active:
            st.session_state.chatbot_active = True
        
        # Chatbot toggle (simplified for advanced modes)
        col_chat1, col_chat2 = st.columns([2, 1])
        
        with col_chat1:
            st.success("💬 Clarification Assistant Ready - Start typing your research question below!")
        
        with col_chat2:
            col_reset, col_toggle = st.columns(2)
            with col_reset:
                if st.button("🔄 Reset"):
                    st.session_state.chat_messages = []
                    clarification_chatbot.reset_conversation()
                    st.session_state.chat_timestamp += 1
                    st.rerun()
            with col_toggle:
                if st.button("⚡ Skip Chat"):
                    st.session_state.chatbot_active = False
                    st.rerun()
    
        # Chatbot Interface - Only for advanced modes
        if st.session_state.chatbot_active:
            st.markdown("---")
            
            # Chat container with better styling for advanced modes
            with st.expander("💬 **Clarification Chat** - Get help refining your research query", expanded=True):
                # Display chat history
                if st.session_state.chat_messages:
                    for message in st.session_state.chat_messages:
                        if message["role"] == "user":
                            with st.chat_message("user"):
                                st.write(message["content"])
                        else:
                            with st.chat_message("assistant"):
                                st.markdown(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown("""👋 **Welcome to Advanced Research Mode!** 

I'm your clarification assistant. I'll help you refine your research question to get the best results from our advanced research capabilities.

**What would you like to research today?** Be as specific or as broad as you'd like - I'll help you narrow it down.""")
            
            # Chat input
            chat_input = st.chat_input("💭 Describe what you want to research... (I'll help make it more specific)")
            
            if chat_input:
                # Add user message
                st.session_state.chat_messages.append({"role": "user", "content": chat_input})
                st.session_state.chat_timestamp += 1
                
                # Get bot response
                with st.spinner("🤔 Analyzing your research needs..."):
                    import asyncio
                    try:
                        response = asyncio.run(clarification_chatbot.chat(chat_input))
                        
                        # Add bot response
                        st.session_state.chat_messages.append({
                            "role": "assistant", 
                            "content": response["response"]
                        })
                        
                        # Check if clarification is complete
                        if response["is_complete"]:
                            st.success("🎉 **Perfect!** Your research query is now well-defined and ready for advanced research.")
                            if response["research_brief"]:
                                st.markdown("### 📋 **Final Research Brief**")
                                st.markdown(response["research_brief"])
                                
                                # Auto-populate the query field
                                refined_query = response["research_brief"]
                                st.session_state.suggested_query = refined_query
                                
                                col_action1, col_action2 = st.columns(2)
                                with col_action1:
                                    if st.button("🚀 **Start Research with This Query**", type="primary"):
                                        st.session_state.chatbot_active = False
                                        st.rerun()
                                with col_action2:
                                    if st.button("✏️ **Continue Refining**"):
                                        st.session_state.chat_messages.append({
                                            "role": "assistant",
                                            "content": "Great! What else would you like to adjust about your research focus?"
                                        })
                                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"💥 Chat temporarily unavailable: {str(e)}")
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": "I'm having trouble right now. Could you try rephrasing your question?"
                        })
                
                st.rerun()
            
            st.markdown("---")
    
with col2:
    st.markdown("### 🎯 Quick Examples")

with col1:
    # Clear input using dynamic key approach
    current_key = f"query_input_{st.session_state.input_key}"
    
    # Debug info right above the text area
    st.caption(f"🔧 Debug: Using key '{current_key}', clear_input={st.session_state.clear_input}")
    
    # Check if we have a suggested query from chatbot
    default_value = ""
    if hasattr(st.session_state, 'suggested_query') and st.session_state.suggested_query:
        default_value = st.session_state.suggested_query
        # Clear the suggestion after using it
        delattr(st.session_state, 'suggested_query')
    
    # Adjust placeholder and help text based on mode
    if is_advanced_mode:
        if st.session_state.chatbot_active:
            placeholder_text = "Use the clarification chat above to refine your query, or enter your research question directly here..."
            help_text = "🎯 Advanced mode: Use the chat above for guided query refinement, or enter your question directly"
        else:
            placeholder_text = "Enter your refined research question from the clarification chat..."
            help_text = "✅ Your query has been refined - ready for advanced research!"
    else:
        placeholder_text = "Be specific and detailed for comprehensive results..."
        help_text = "💡 Tip: The more specific your question, the better the research results"
    
    query = st.text_area(
        "Enter your research question:",
        value=default_value,
        height=140,
        placeholder=placeholder_text,
        help=help_text,
        key=current_key
    )
    
    # Show what the query variable contains
    if query:
        st.caption(f"📝 Current input: '{query}' (length: {len(query)})")
        if is_advanced_mode and not st.session_state.chatbot_active:
            st.info("💡 **Tip**: For advanced modes, consider using the clarification chat to optimize your query further.")
    else:
        st.caption("📝 Input is empty")

with col2:
    # Mode-specific examples
    if mode == "Enhanced MCP Research":
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #1a202c;">
            <strong>📊 Statistical Examples:</strong><br>
            • Compare GDP trends between countries<br>
            • Analyze unemployment rates by region<br>
            • Health outcomes by demographics<br><br>
            <strong>📁 Document Examples:</strong><br>
            • Analyze local research files<br>
            • Extract insights from reports<br>
            • Compare multiple documents
        </div>
        """, unsafe_allow_html=True)
    elif mode == "Basic Research":
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #1a202c;">
            <strong>🌐 Web Research Examples:</strong><br>
            • Latest tech developments<br>
            • Market analysis trends<br>
            • Scientific breakthroughs<br>
            • Industry news summaries
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #1a202c;">
            <strong>🔬 Research Examples:</strong><br>
            • Complex analysis topics<br>
            • Multi-source investigations<br>
            • Comprehensive reports<br>
            • Detailed comparisons
        </div>
        """, unsafe_allow_html=True)

# Enhanced research history section
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

if st.session_state.research_history:
    st.markdown("### 📚 Research History")
    with st.expander(f"📋 View {len(st.session_state.research_history)} Recent Queries", expanded=False):
        for i, (timestamp, past_mode, past_query, _) in enumerate(reversed(st.session_state.research_history[-10:])):
            col_time, col_mode, col_query = st.columns([1, 1, 3])
            with col_time:
                st.markdown(f"**{timestamp.split()[1]}**")
            with col_mode:
                mode_icons = {
                    "Basic Research": "🔍",
                    "MCP Research": "📁", 
                    "Enhanced MCP Research": "🌍",
                    "Full Research": "⚡"
                }
                st.markdown(f"{mode_icons.get(past_mode, '🔬')} {past_mode}")
            with col_query:
                # Truncate long queries
                display_query = past_query[:100] + "..." if len(past_query) > 100 else past_query
                if st.button(f"🔄 Rerun: {display_query}", key=f"rerun_{i}", help=f"Click to rerun: {past_query}"):
                    st.session_state.rerun_query = past_query
                    st.session_state.rerun_mode = past_mode
                    st.rerun()
            if i < min(9, len(st.session_state.research_history)-1):
                st.markdown("<hr style='margin: 0.5rem 0; border: 1px solid #eee;'>", unsafe_allow_html=True)

# Handle query rerun
if hasattr(st.session_state, 'rerun_query'):
    query = st.session_state.rerun_query
    delattr(st.session_state, 'rerun_query')
    if hasattr(st.session_state, 'rerun_mode'):
        delattr(st.session_state, 'rerun_mode')

# Virtual Research Assistant
if query and len(query.strip()) > 10:  # Only show for substantive queries
    with st.expander("🤖 Virtual Research Assistant - Get Scoping Help", expanded=False):
        st.markdown("**Let me help optimize your research query for better results!**")
        
        try:
            # Quick tips
            quick_tips = virtual_assistant.get_quick_tips(query)
            if quick_tips:
                st.markdown("### 💡 Quick Tips")
                for tip in quick_tips:
                    st.info(tip)
            
            # Mode suggestion
            suggested_mode, mode_reason = virtual_assistant.suggest_research_mode(query)
            if suggested_mode != mode:
                st.markdown("### 🎯 Mode Recommendation")
                st.warning(f"💡 **Suggested Mode**: {suggested_mode} - {mode_reason}")
            else:
                st.success(f"✅ **Good Mode Choice**: {mode} is perfect for this query!")
                
        except Exception as e:
            st.error(f"Virtual Assistant temporarily unavailable: {str(e)}")
            st.info("💡 **Tip**: Try being more specific with your query for better results.")
        
        # Advanced scoping analysis
        if st.button("🧠 Get AI-Powered Scoping Suggestions", help="Get 3 optimized versions of your query"):
            with st.spinner("🤖 Analyzing your query and generating suggestions..."):
                try:
                    suggestions = virtual_assistant.analyze_query(query)
                    
                    if suggestions and 'suggestions' in suggestions:
                        st.markdown("### 📝 Optimized Query Suggestions")
                    
                    for i, suggestion in enumerate(suggestions['suggestions'], 1):
                        with st.container():
                            st.markdown(f"**Option {i}: {suggestion['research_mode']}**")
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.code(suggestion['suggested_query'], language=None)
                                st.caption(f"💡 {suggestion['rationale']}")
                                st.caption(f"🎯 Expected: {suggestion['estimated_improvement']}")
                                
                            with col2:
                                if st.button(f"Use Option {i}", key=f"use_suggestion_{i}"):
                                    # Update the query with the suggestion
                                    st.session_state[f'text_area_{st.session_state.input_key}'] = suggestion['suggested_query']
                                    st.session_state.suggested_query = suggestion['suggested_query']
                                    st.success(f"✅ Applied Option {i}!")
                                    st.rerun()
                            
                            if i < len(suggestions['suggestions']):
                                st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
                    
                    # General advice
                    if 'general_advice' in suggestions:
                        st.markdown("### 🎓 General Advice")
                        st.info(suggestions['general_advice'])
                    
                    # Complexity score
                    if 'complexity_score' in suggestions:
                        complexity = int(suggestions.get('complexity_score', 3))
                        complexity_labels = {
                            1: "Very Simple 🟢",
                            2: "Simple 🟢", 
                            3: "Moderate 🟡",
                            4: "Complex 🟠",
                            5: "Very Complex 🔴"
                        }
                        st.metric("Query Complexity", complexity_labels.get(complexity, "Unknown"))
                    else:
                        st.warning("⚠️ Could not generate AI suggestions. Please try again or refine your query.")
                        
                except Exception as e:
                    st.error(f"AI suggestions temporarily unavailable: {str(e)}")
                    st.info("💡 **Manual Tips**: Try adding time periods, geographic constraints, or specific focus areas to your query.")

# Enhanced research execution section
st.markdown("---")

# Research button with loading state
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Show different button states based on processing status
    if st.session_state.get('processing', False):
        st.button(
            f"🔄 {mode} Running...",
            type="secondary",
            use_container_width=True,
            disabled=True,
            help="Research is currently in progress. Please wait for completion."
        )
        research_button = False  # Don't trigger new research
    else:
        research_button = st.button(
            f"🔬 Start {mode}",
            type="primary",
            use_container_width=True,
            help=f"Click to begin research using {mode}"
        )

# Research execution with enhanced progress display
if research_button:
    if query and query.strip():
        # Store the query and increment key to clear input
        research_query = query.strip()
        st.session_state.submitted_query = research_query
        st.session_state.clear_input = True
        st.session_state.input_key += 1  # This will force a new text area with empty value
        
        # Add comprehensive debugging for button click
        st.sidebar.success("🔄 BUTTON CLICKED!")
        st.sidebar.write(f"Original query: '{query}'")
        st.sidebar.write(f"Stored query: '{research_query}'")
        st.sidebar.write(f"Previous input_key: {st.session_state.input_key - 1}")
        st.sidebar.write(f"New input_key: {st.session_state.input_key}")
        st.sidebar.write(f"clear_input flag: {st.session_state.clear_input}")
        
        # Trigger rerun to clear the input immediately
        st.rerun()

# Check if we have a submitted query to process
if st.session_state.submitted_query and not st.session_state.get('processing', False):
    research_query = st.session_state.submitted_query
    st.session_state.processing = True
    
    # Add to research history
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Enhanced progress messages and indicators with estimated times
    progress_info = {
        "Basic Research": {
            "message": "🔍 Searching the web and analyzing sources...",
            "avatar": "🔍",
            "estimated_time": "15-30 seconds",
            "steps": [
                {"icon": "🌐", "text": "Querying web sources", "time": "8s"},
                {"icon": "📄", "text": "Analyzing content", "time": "12s"},
                {"icon": "✅", "text": "Compiling results", "time": "5s"}
            ]
        },
        "MCP Research": {
            "message": "📁 Analyzing local files and documents...",
            "avatar": "📁",
            "estimated_time": "20-40 seconds",
            "steps": [
                {"icon": "📂", "text": "Accessing local files", "time": "5s"},
                {"icon": "🔍", "text": "Extracting content", "time": "15s"},
                {"icon": "📊", "text": "Analyzing data", "time": "20s"}
            ]
        },
        "Enhanced MCP Research": {
            "message": "🌍 Accessing local files and Data Commons statistical data...",
            "avatar": "🌍",
            "estimated_time": "45-90 seconds",
            "steps": [
                {"icon": "📁", "text": "Loading local files", "time": "10s"},
                {"icon": "📊", "text": "Querying Data Commons", "time": "25s"},
                {"icon": "🔬", "text": "Cross-referencing sources", "time": "20s"},
                {"icon": "📈", "text": "Generating insights", "time": "15s"}
            ]
        },
        "Full Research": {
            "message": "⚡ Conducting comprehensive multi-source research...",
            "avatar": "🧠",
            "estimated_time": "60-120 seconds",
            "steps": [
                {"icon": "🌐", "text": "Web research", "time": "30s"},
                {"icon": "📄", "text": "Document analysis", "time": "25s"},
                {"icon": "🧠", "text": "Synthesis", "time": "20s"},
                {"icon": "📋", "text": "Report generation", "time": "15s"}
            ]
        }
    }
    
    current_progress = progress_info.get(mode, {
        "message": "🔬 Conducting research...",
        "steps": ["🔍 Analyzing query", "📊 Processing data", "✅ Generating results"]
    })
    
    # Enhanced progress container with animations and estimated time
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-title">🔬 Research in Progress</div>
        <div class="research-avatar">{current_progress['avatar']}</div>
        <div class="status-message">
            <strong>{current_progress['message']}</strong><br>
            <small>⏱️ Estimated time: {current_progress['estimated_time']}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create containers for dynamic updates
    progress_bar = st.progress(0)
    status_text = st.empty()
    steps_container = st.empty()
    time_container = st.empty()
    
    # Disable the research button during processing
    st.session_state.processing = True
    
    # Initialize timing
    start_time = time.time()
    
    try:
        start_time = time.time()
        total_steps = len(current_progress["steps"])
        
        # Show initial step overview
        steps_html = ""
        for j, step_info in enumerate(current_progress["steps"]):
            steps_html += f'<div class="step-item step-pending">{step_info["icon"]} {step_info["text"]} <small>(~{step_info["time"]})</small></div>'
        
        steps_container.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin: 1rem 0;">
            <h4 style="margin-top: 0; color: #333;">📋 Research Steps:</h4>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)
        
        # Show step 1: Starting research
        progress_bar.progress(0.2)
        status_text.markdown(f"**🔄 {current_progress['steps'][0]['icon']} {current_progress['steps'][0]['text']}...**")
        time_container.markdown(f"⏱️ Starting research... | Step 1 of {total_steps}")
        
        # Update step visualization for step 1
        steps_html = f'<div class="step-item step-current">🔄 {current_progress["steps"][0]["icon"]} {current_progress["steps"][0]["text"]} <small>(in progress...)</small></div>'
        for j in range(1, len(current_progress["steps"])):
            s_info = current_progress["steps"][j]
            steps_html += f'<div class="step-item step-pending">⏳ {s_info["icon"]} {s_info["text"]} <small>(~{s_info["time"]})</small></div>'
        
        steps_container.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin: 1rem 0;">
            <h4 style="margin-top: 0; color: #333;">📋 Research Steps:</h4>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)
        
        # Start cost tracking session
        session_id = cost_tracker.start_session(mode, research_query)
        
        # Execute research
        research_functions = {
            "Basic Research": run_basic_research,
            "MCP Research": run_mcp_research,
            "Enhanced MCP Research": run_enhanced_mcp_research,
            "Full Research": run_full_research
        }
        
        research_func = research_functions[mode]
        
        # Show step 2: Executing main research
        progress_bar.progress(0.4)
        if len(current_progress["steps"]) > 1:
            status_text.markdown(f"**� {current_progress['steps'][1]['icon']} {current_progress['steps'][1]['text']}...**")
            time_container.markdown(f"⏱️ Research in progress... | Step 2 of {total_steps}")
        
        # Execute research with progress tracking
        result = asyncio.run(research_func(research_query))
        
        # Show step 3: Finalizing (if it exists)
        if len(current_progress["steps"]) > 2:
            progress_bar.progress(0.8)
            status_text.markdown(f"**🔄 {current_progress['steps'][2]['icon']} {current_progress['steps'][2]['text']}...**")
            time_container.markdown(f"⏱️ Finalizing results... | Step 3 of {total_steps}")
            time.sleep(1)  # Brief pause for finalization visual
        
        # Final step completion
        progress_bar.progress(0.95)
        status_text.markdown("**🔧 Generating final report...**")
        time_container.markdown("⏳ Almost done... | Final processing")
        
        # End cost tracking session
        cost_session = cost_tracker.end_session()
        
        # Complete progress with clear completion state
        total_time = int(time.time() - start_time)
        progress_bar.progress(1.0)
        status_text.markdown("**🎉 Research completed successfully!**")
        time_container.markdown(f"✅ Completed in {total_time}s | Ready to view results")
        
        # Display cost summary if available
        if cost_session:
            st.markdown("### 💰 Research Cost Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Cost",
                    value=f"${cost_session.total_cost_usd:.4f}",
                    help="Actual cost for this research session"
                )
            
            with col2:
                st.metric(
                    label="Input Tokens",
                    value=f"{cost_session.total_input_tokens:,}",
                    help="Tokens sent to AI models"
                )
            
            with col3:
                st.metric(
                    label="Output Tokens",
                    value=f"{cost_session.total_output_tokens:,}",
                    help="Tokens generated by AI models"
                )
            
            with col4:
                st.metric(
                    label="Duration",
                    value=f"{cost_session.duration_seconds:.1f}s",
                    help="Total research time"
                )
            
            # Cost breakdown in expander
            with st.expander("📊 Detailed Cost Breakdown", expanded=False):
                for i, call in enumerate(cost_session.model_calls, 1):
                    st.write(f"**Call {i}** - {call.model_name} ({call.operation})")
                    st.write(f"└ Input: {call.input_tokens:,} tokens | Output: {call.output_tokens:,} tokens | Cost: ${call.cost_usd:.4f}")
                
                if cost_session.total_cost_usd > 0.01:
                    st.warning("💡 **Cost Optimization Tip**: For frequent queries, consider using Basic Research mode for lower costs.")
                else:
                    st.success("💰 **Cost Efficient**: This query was processed very cost-effectively!")
        
        # Show clear completion state with all steps completed
        steps_html = ""
        for step_info in current_progress["steps"]:
            steps_html += f'<div class="step-item step-completed">✅ {step_info["icon"]} {step_info["text"]} <small>Done</small></div>'
        
        # Update steps container with final completion state
        steps_container.markdown(f"""
        <div class="research-complete" style="
            background: linear-gradient(135deg, #e8f5e8, #ffffff);
            border: 2px solid #4caf50;
            border-radius: 12px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
        ">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎉</div>
                <div style="color: #2e7d32; font-weight: 700; font-size: 1.4rem; margin-bottom: 0.5rem;">
                    Research Successfully Completed!
                </div>
                <div style="color: #4caf50; font-size: 1rem; margin-bottom: 1rem;">
                    Generated {len(result.split())} words in {total_time} seconds
                </div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #c8e6c9;">
                <h4 style="margin-top: 0; color: #2e7d32; text-align: center;">📋 Completed Steps:</h4>
                {steps_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Store in history
        st.session_state.research_history.append((timestamp, mode, research_query, result))
        
        # Enhanced results display with completion confirmation
        st.markdown("---")
        st.markdown("""
        <div class="results-container">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="display: inline-block; background: #e8f5e8; color: #2e7d32; padding: 0.5rem 1.5rem; border-radius: 25px; border: 2px solid #4caf50; font-weight: bold; margin-bottom: 1rem;">
                    ✅ RESEARCH COMPLETED SUCCESSFULLY
                </div>
            </div>
            <h2 style="color: #667eea; margin-top: 0;">📊 Research Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Results with copy button
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(result)
        with col2:
            if st.button("📋 Copy Results", help="Copy results to clipboard"):
                st.code(result, language="markdown")
        
        # Success metrics with enhanced styling and completion status
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; border: 1px solid #2196f3; margin: 1rem 0;">
            <div style="text-align: center; font-weight: bold; color: #1976d2; margin-bottom: 0.5rem;">
                🎯 Research Session Summary
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Research Mode", mode)
        with col2:
            st.metric("📝 Query Length", f"{len(research_query)} chars")
        with col3:
            st.metric("📊 Result Length", f"{len(result)} chars")
        with col4:
            st.metric("⏱️ Processing Time", f"{total_time}s")
        
        # Enhanced success message with completion confirmation
        st.success(f"🎉 Research completed successfully using **{mode}**! Generated comprehensive analysis in {total_time} seconds.")
        
        # Only now clean up the progress indicators after results are fully displayed
        time.sleep(0.5)  # Brief pause to ensure results are rendered
        progress_bar.empty()
        status_text.empty()
        time_container.empty()
        # Keep the completion steps visible for reference
        
        # Reset processing flag
        st.session_state.processing = False
        
        # Reset all flags after completion
        st.session_state.submitted_query = ""
        st.session_state.processing = False
        st.session_state.clear_input = False
        
    except Exception as e:
        # Clean up progress display
        progress_bar.progress(0)
        status_text.empty()
        steps_container.empty()
        if 'time_container' in locals():
            time_container.empty()
        
        # Enhanced error reporting with retry functionality
        import traceback
        error_details = traceback.format_exc()
        
        # Calculate error time safely
        error_time = int(time.time() - start_time)
        
        # Reset processing flag
        st.session_state.processing = False
        
        # Don't clear the query on error - allow retry
        # st.session_state.submitted_query = ""
        # st.session_state.clear_input = False
        
        # Enhanced error display with specific API quota handling
        if "RateLimitError" in str(e) or "429" in str(e) or "quota" in str(e).lower():
            st.error(f"🚫 API Quota Exceeded ({error_time}s): You've reached your OpenAI API limit")
            
            # Show quota-specific help
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: #fff3e0; border: 2px solid #ff9800; border-radius: 10px; padding: 1.5rem; margin: 1rem 0;">
                    <h4 style="color: #f57c00; margin-top: 0;">💳 OpenAI API Quota Exceeded</h4>
                    <p style="color: #e65100; margin-bottom: 1rem;">
                        Your OpenAI API has reached its usage limit. This is common when testing research applications.
                    </p>
                    <div style="background: #f0f8ff; border: 1px solid #2196f3; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                        <strong style="color: #1976d2;">🔧 Immediate Solutions:</strong><br>
                        • <strong>Add Credits:</strong> Visit <a href="https://platform.openai.com/account/billing" target="_blank" style="color: #1976d2; text-decoration: none;">OpenAI Billing Dashboard</a><br>
                        • <strong>Check Usage:</strong> Review your <a href="https://platform.openai.com/usage" target="_blank" style="color: #1976d2; text-decoration: none;">current usage</a><br>
                        • <strong>Upgrade Plan:</strong> Consider a higher tier for more credits<br>
                        • <strong>Alternative:</strong> You have Anthropic Claude configured as backup
                    </div>
                    <div style="background: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; padding: 1rem;">
                        <strong style="color: #2e7d32;">💡 Temporary Workarounds:</strong><br>
                        • Use Basic Research (fewer API calls needed)<br>
                        • Try shorter, simpler queries<br>
                        • Wait for monthly quota reset<br>
                        • Switch to Anthropic Claude model in settings
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 Retry Basic Research", type="secondary", use_container_width=True, help="Switch to Basic Research mode"):
                    st.session_state.submitted_query = research_query
                    st.session_state.processing = False
                    st.info("💡 Try Basic Research - uses fewer API calls")
                    st.rerun()
                    
                if st.button("💳 Open Billing", type="secondary", use_container_width=True):
                    st.markdown('[🔗 OpenAI Billing →](https://platform.openai.com/account/billing)', unsafe_allow_html=True)
                    
                if st.button("📊 Check Usage", type="secondary", use_container_width=True):
                    st.markdown('[🔗 Usage Dashboard →](https://platform.openai.com/usage)', unsafe_allow_html=True)
                    
        elif "AuthenticationError" in str(e) or "401" in str(e):
            st.error(f"🔐 Authentication Error ({error_time}s): Invalid API key")
            st.markdown("""
            <div style="background: #ffebee; border: 2px solid #f44336; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <strong style="color: #c62828;">🔑 API Key Problem:</strong><br>
                • Verify your .env file contains valid API keys<br>
                • Check for extra spaces or line breaks in keys<br>
                • Ensure keys haven't expired or been revoked<br>
                • Try regenerating keys in your API dashboard
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Research failed after {error_time}s: {str(e)[:200]}...")
        
        # Show detailed error in debug sidebar
        st.sidebar.error("🚨 RESEARCH ERROR")
        if "quota" in str(e).lower() or "429" in str(e):
            st.sidebar.warning("💳 OpenAI quota exceeded. Try Basic Research mode or add credits.")
        st.sidebar.code(error_details[:1000] + "..." if len(error_details) > 1000 else error_details, language="python")
        
        # Enhanced error container with retry option
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: #ffebee; border: 2px solid #f44336; border-radius: 10px; padding: 1.5rem; margin: 1rem 0;">
                <h4 style="color: #c62828; margin-top: 0;">🚨 Research Failed</h4>
                <p style="color: #d32f2f; margin-bottom: 1rem;">
                    The research process encountered an error after {error_time} seconds.
                </p>
                <details style="margin-bottom: 1rem;">
                    <summary style="color: #d32f2f; cursor: pointer; font-weight: bold;">🔍 View Technical Details</summary>
                    <pre style="background: #f5f5f5; padding: 1rem; border-radius: 5px; font-size: 0.8rem; overflow-x: auto; margin-top: 0.5rem; color: #666;">{str(e)}</pre>
                </details>
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem;">
                    <strong>🔧 Troubleshooting Tips:</strong><br>
                    • Check your .env file for required API keys<br>
                    • Ensure all dependencies are installed<br>
                    • Try a simpler query to test connectivity<br>
                    • Check the debug panel for detailed error information<br>
                    • Try again - temporary network issues are common
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Retry button
            if st.button("🔄 Retry Research", type="secondary", use_container_width=True):
                st.session_state.submitted_query = research_query  # Reset for retry
                st.session_state.processing = False
                st.rerun()
            
            # Simplify query button
            if st.button("📝 Simplify Query", type="secondary", use_container_width=True):
                simplified_query = f"Simple overview of {research_query.split()[:5]}"
                st.session_state.submitted_query = " ".join(simplified_query.split()[:10])
                st.session_state.processing = False
                st.rerun()
        
        # Allow users to see the full error
        with st.expander("🔍 View Full Error Details"):
            st.code(error_details, language="python")

# Show warning if no query entered
elif research_button and not query:
    st.warning("⚠️ Please enter a research query before starting.")
    st.info("💡 **Tip**: Use the Quick Examples panel for inspiration!")

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #666; font-size: 0.9rem;">
    <p>🔬 <strong>Deep Research from Scratch</strong> - Advanced AI Research Platform</p>
    <p>Built with ❤️ using <a href="https://streamlit.io" style="color: #667eea;">Streamlit</a>, 
       <a href="https://langchain.com" style="color: #667eea;">LangChain</a>, and 
       <a href="https://python.langchain.com/docs/langgraph" style="color: #667eea;">LangGraph</a></p>
</div>
""", unsafe_allow_html=True)