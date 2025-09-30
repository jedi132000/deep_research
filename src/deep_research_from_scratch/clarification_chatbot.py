"""
Conversational Clarification Chatbot for Research Query Refinement
"""

import asyncio
from typing import List, Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from .cost_tracker import cost_tracker
import streamlit as st


class ClarificationChatbot:
    """Interactive chatbot for refining research queries through conversation"""
    
    def __init__(self):
        self.model = None
        self.conversation_history: List[Dict[str, str]] = []
        self.research_brief: Optional[str] = None
        self.is_ready_for_research = False
        
    def _ensure_model_loaded(self):
        """Lazy load the model to avoid initialization issues"""
        if self.model is None:
            self.model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=800
            )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the clarification chatbot"""
        return """You are a helpful research assistant that helps users clarify and refine their research questions through conversation.

Your role:
1. Ask clarifying questions to understand what the user really wants to research
2. Help them be more specific about scope, timeframe, geography, or focus areas
3. Suggest improvements to make their query more research-friendly
4. When their query is well-defined, generate a clear research brief

Guidelines:
- Be conversational and friendly
- Ask one focused question at a time
- Provide examples when helpful
- Don't overwhelm with too many questions
- When the query is clear enough, say "Great! I think we have a clear research direction now." and provide a research brief

Current conversation context: The user wants to do research but needs help clarifying their query to get the best results."""

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and return the chatbot's response
        
        Returns:
        - response: The chatbot's message
        - is_complete: Whether the clarification is complete
        - research_brief: If complete, the finalized research brief
        """
        self._ensure_model_loaded()
        
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user", 
                "content": user_message,
                "timestamp": st.session_state.get('chat_timestamp', 0)
            })
            
            # Build message history for the model
            messages = [SystemMessage(content=self.get_system_prompt())]
            
            # Add conversation history
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Get response from model with cost tracking
            with cost_tracker.track_model_usage("gpt-4o-mini", "clarification_chat"):
                response = await self.model.ainvoke(messages)
            
            bot_response = response.content
            
            # Add bot response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": st.session_state.get('chat_timestamp', 0) + 1
            })
            
            # Check if clarification is complete
            completion_indicators = [
                "great! i think we have a clear research direction",
                "research brief:",
                "ready to research:",
                "here's your research brief",
                "final research question:",
                "research scope:"
            ]
            
            is_complete = any(indicator in bot_response.lower() for indicator in completion_indicators)
            
            if is_complete:
                self.is_ready_for_research = True
                # Extract or generate research brief
                self.research_brief = self._extract_research_brief(bot_response, user_message)
            
            return {
                "response": bot_response,
                "is_complete": is_complete,
                "research_brief": self.research_brief if is_complete else None,
                "conversation_length": len(self.conversation_history)
            }
            
        except Exception as e:
            error_response = f"I'm having trouble processing that right now. Could you try rephrasing your question? (Error: {str(e)})"
            
            self.conversation_history.append({
                "role": "assistant",
                "content": error_response,
                "timestamp": st.session_state.get('chat_timestamp', 0) + 1
            })
            
            return {
                "response": error_response,
                "is_complete": False,
                "research_brief": None,
                "conversation_length": len(self.conversation_history)
            }
    
    def _extract_research_brief(self, bot_response: str, user_context: str) -> str:
        """Extract or generate a research brief from the conversation"""
        
        # If the response already contains a clear research brief, use it
        if "research brief:" in bot_response.lower():
            parts = bot_response.lower().split("research brief:")
            if len(parts) > 1:
                return parts[1].strip()
        
        # Otherwise, generate a brief from the conversation context
        full_context = " ".join([msg["content"] for msg in self.conversation_history if msg["role"] == "user"])
        
        research_brief = f"""## Research Brief

**Primary Question**: {user_context}

**Clarified Scope**: Based on our conversation, this research will focus on the specific aspects and context we discussed.

**Research Context**: {full_context[:200]}...

**Ready for Investigation**: This query has been refined and is ready for comprehensive research."""

        return research_brief
    
    def reset_conversation(self):
        """Reset the chatbot for a new conversation"""
        self.conversation_history = []
        self.research_brief = None
        self.is_ready_for_research = False
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation state"""
        return {
            "message_count": len(self.conversation_history),
            "is_ready": self.is_ready_for_research,
            "has_brief": self.research_brief is not None,
            "last_message": self.conversation_history[-1] if self.conversation_history else None
        }
    
    def suggest_starter_questions(self) -> List[str]:
        """Provide starter questions to help users begin the conversation"""
        return [
            "What specific aspect of [topic] are you most interested in?",
            "What time period should this research cover?", 
            "Are you looking for a particular geographic focus?",
            "What will you use this research for?",
            "Do you have any specific requirements or constraints?",
            "What level of detail do you need?"
        ]


# Global instance for the app
clarification_chatbot = ClarificationChatbot()