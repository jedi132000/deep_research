"""
In-App Feedback System for Deep Research Pro
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional

class FeedbackCollector:
    """Collect and manage user feedback within the app"""
    
    def __init__(self):
        self.feedback_file = "user_feedback.json"
    
    def show_post_research_feedback(self, research_mode: str, query: str, result_length: int):
        """Show contextual feedback after successful research completion"""
        
        st.markdown("---")
        st.markdown("### 📝 **How was your research experience?**")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Quick rating system
            st.markdown("**Rate this research session:**")
            rating_cols = st.columns(5)
            
            rating = None
            with rating_cols[0]:
                if st.button("⭐", key="rating_1"):
                    rating = 1
            with rating_cols[1]:
                if st.button("⭐⭐", key="rating_2"):
                    rating = 2
            with rating_cols[2]:
                if st.button("⭐⭐⭐", key="rating_3"):
                    rating = 3
            with rating_cols[3]:
                if st.button("⭐⭐⭐⭐", key="rating_4"):
                    rating = 4
            with rating_cols[4]:
                if st.button("⭐⭐⭐⭐⭐", key="rating_5"):
                    rating = 5
            
            # Quick feedback buttons
            st.markdown("**Quick feedback:**")
            feedback_cols = st.columns(3)
            
            feedback_type = None
            with feedback_cols[0]:
                if st.button("👍 Excellent Results", key="feedback_excellent"):
                    feedback_type = "excellent"
            with feedback_cols[1]:
                if st.button("💡 Needs Citations", key="feedback_citations"):
                    feedback_type = "citations"
            with feedback_cols[2]:
                if st.button("⚡ Too Slow", key="feedback_speed"):
                    feedback_type = "speed"
            
            # Detailed feedback (expandable)
            with st.expander("💬 **Share Detailed Feedback** (Help us improve!)", expanded=False):
                detailed_feedback = st.text_area(
                    "Tell us more about your experience:",
                    placeholder="What worked well? What could be better? Any specific features you'd like to see?",
                    height=100
                )
                
                feedback_category = st.selectbox(
                    "Category:",
                    ["General Experience", "Citation Quality", "Research Depth", "Speed/Performance", 
                     "UI/UX", "Cost/Pricing", "Feature Request", "Bug Report"]
                )
                
                contact_ok = st.checkbox("It's OK to contact me about this feedback (optional)")
                
                if st.button("📤 Submit Feedback", type="primary"):
                    if detailed_feedback or rating or feedback_type:
                        self.save_feedback({
                            "timestamp": datetime.now().isoformat(),
                            "research_mode": research_mode,
                            "query": query[:100] + "..." if len(query) > 100 else query,
                            "result_length": result_length,
                            "rating": rating,
                            "feedback_type": feedback_type,
                            "detailed_feedback": detailed_feedback,
                            "category": feedback_category,
                            "contact_ok": contact_ok
                        })
                        st.success("🎉 Thank you for your feedback! This helps us improve Deep Research Pro.")
                        st.balloons()
                    else:
                        st.warning("Please provide a rating or feedback before submitting.")
    
    def show_academic_citation_helper(self):
        """Show enhanced citation and academic formatting options"""
        
        with st.expander("📚 **Academic Citation & Quality Tools**", expanded=False):
            st.markdown("""
            **Improve Academic Standards:**
            
            🎯 **Citation Styles Available:**
            - APA (American Psychological Association)
            - MLA (Modern Language Association)  
            - Chicago/Turabian
            - IEEE (Institute of Electrical and Electronics Engineers)
            - Harvard Referencing
            """)
            
            citation_style = st.selectbox(
                "Select preferred citation style:",
                ["APA", "MLA", "Chicago", "IEEE", "Harvard"],
                help="This will format any citations found in your research"
            )
            
            academic_level = st.selectbox(
                "Academic Level:",
                ["Undergraduate", "Graduate", "PhD/Research", "Professional"],
                help="Adjusts depth and rigor of research approach"
            )
            
            st.markdown("""
            **📋 Academic Quality Features:**
            - ✅ Source credibility assessment
            - ✅ Peer-reviewed source prioritization  
            - ✅ Quote extraction with page numbers
            - ✅ Bibliography generation
            - ✅ Fact-checking cross-references
            """)
            
            if st.button("🎓 Enable Academic Mode", key="academic_mode"):
                st.session_state.academic_mode = {
                    "citation_style": citation_style,
                    "academic_level": academic_level,
                    "enabled": True
                }
                st.success(f"✅ Academic mode enabled with {citation_style} citations for {academic_level} level research.")
    
    def save_feedback(self, feedback_data: Dict):
        """Save feedback to local file for analysis"""
        try:
            # Load existing feedback
            try:
                with open(self.feedback_file, 'r') as f:
                    all_feedback = json.load(f)
            except FileNotFoundError:
                all_feedback = []
            
            # Add new feedback
            all_feedback.append(feedback_data)
            
            # Save back to file
            with open(self.feedback_file, 'w') as f:
                json.dump(all_feedback, f, indent=2)
                
        except Exception as e:
            st.error(f"Could not save feedback: {str(e)}")
    
    def show_pricing_flexibility(self):
        """Address pricing concerns with transparent options"""
        
        with st.expander("💰 **Flexible Pricing & Cost Management**", expanded=False):
            st.markdown("""
            **💡 Cost-Saving Tips:**
            
            🎯 **Smart Usage:**
            - Use **Basic Research** for simple queries (~$0.02)
            - Try **Advanced Research** before going Pro (~$0.05)
            - Monitor daily costs in sidebar
            - Be specific in queries to avoid re-runs
            
            💳 **Pricing Flexibility:**
            - Pay-per-use model (no subscriptions)
            - Real-time cost estimates
            - Daily usage tracking
            - Transparent token pricing
            
            🎁 **Value Features:**
            - Export results (Markdown, JSON)
            - Conversation history
            - Professional templates
            - Academic citation tools
            """)
            
            # Usage analytics
            if hasattr(st.session_state, 'total_research_cost'):
                st.metric("Session Cost", f"${st.session_state.total_research_cost:.4f}")
            else:
                st.info("💡 Start researching to see cost tracking in action!")
    
    def show_improvement_changelog(self):
        """Show recent improvements based on user feedback"""
        
        with st.expander("🔄 **Recent Updates from User Feedback**", expanded=False):
            st.markdown("""
            **✨ Latest Improvements (Based on Your Input):**
            
            **🎯 This Week:**
            - ✅ Added post-research feedback system
            - ✅ Enhanced academic citation tools
            - ✅ Improved cost transparency
            - ✅ Professional mode names (Basic → Advanced → Pro → Pro+)
            
            **📚 Academic Improvements:**
            - ✅ Citation style selection (APA, MLA, Chicago, etc.)
            - ✅ Academic level customization
            - ✅ Source credibility indicators
            - ✅ Bibliography generation tools
            
            **💰 Cost & Performance:**
            - ✅ Real-time cost estimates
            - ✅ Daily usage tracking
            - ✅ Mode-specific pricing guidance
            - ✅ Optimized token usage
            
            **🎨 User Experience:**
            - ✅ Professional UI with export options
            - ✅ Conversational query clarification
            - ✅ Contextual help and tooltips
            - ✅ Developer mode for advanced users
            """)
            
            st.success("💡 **Keep the feedback coming!** Your input directly shapes our improvements.")


# Global feedback collector instance
feedback_collector = FeedbackCollector()