"""
Recommendation rendering module for the Compliance Assessment Tool.

This module handles the detailed rendering of recommendations based on assessment results.
"""

import streamlit as st
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# This function duplicates one in recommendation_engine.py
def get_recommendation_context(questionnaire: Dict[str, Any], responses: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
    """Get detailed context for recommendations including which questions triggered them."""
    # Identical to recommendation_engine.py's version
    # ...existing code...

def render_detailed_recommendations(section_name: str, contexts: List[Dict[str, Any]]):
    """
    Render detailed recommendations for a section with context
    
    Args:
        section_name: Name of the section
        contexts: List of recommendation contexts for this section
    """
    for context in contexts:
        st.markdown(f"##### Question {context['question_id']}")
        st.write(f"**Q:** {context['question_text']}")
        st.write(f"**Your Response:** {context['response']}")
        st.markdown(f"**Recommendation:** {context['recommendation']}")

def enhance_recommendations_page(questionnaire: Dict[str, Any], results: Dict[str, Any]):
    """
    Add enhanced recommendation details to the recommendations page
    
    Args:
        questionnaire: The questionnaire structure
        results: The assessment results
    """
    # Only proceed if we have responses
    if 'responses' not in st.session_state:
        return
        
    recommendation_context = get_recommendation_context(questionnaire, st.session_state.responses)
    
    # Show detailed explanations
    st.subheader("Recommendation Details")
    st.write("Expand each section to see detailed context for recommendations")
    
    for section, contexts in recommendation_context.items():
        score = results["section_scores"].get(section)
        
        if score is None:
            continue
            
        priority = "high" if score < 0.6 else ("medium" if score < 0.75 else "low")
        priority_emoji = "🔴" if priority == "high" else ("🟠" if priority == "medium" else "🟢")
        
        with st.expander(f"{priority_emoji} {section} - {len(contexts)} recommendations"):
            render_detailed_recommendations(section, contexts)
