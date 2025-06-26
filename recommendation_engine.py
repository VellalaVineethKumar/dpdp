"""
Recommendation Engine for the Compliance Assessment Tool.

This module consolidates recommendation functionality from multiple places:
- Generating recommendations based on assessment results
- Organizing recommendations by priority
- Providing detailed implementation guidance
"""

import logging
from typing import Dict, List, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

def get_recommendation_priority(score: float) -> str:
    """
    Determine recommendation priority based on compliance score
    
    Args:
        score: Compliance score (0.0 to 1.0)
        
    Returns:
        String indicating priority level: 'high', 'medium', or 'low'
    """
    logger.debug(f"Calculating priority for score: {score}")
    
    if score < 0.6:
        logger.debug(f"Score {score} classified as high priority")
        return "high"
    elif score < 0.75:
        logger.debug(f"Score {score} classified as medium priority")
        return "medium"
    else:
        logger.debug(f"Score {score} classified as low priority")
        return "low"

def get_recommendation_context(questionnaire: Dict[str, Any], responses: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get detailed context for recommendations including which questions triggered them.
    
    Args:
        questionnaire: The questionnaire structure
        responses: The user's responses
        
    Returns:
        Dictionary mapping sections to lists of recommendation contexts
    """
    logger.info("Starting recommendation context generation")
    logger.debug(f"Processing questionnaire with {len(questionnaire.get('sections', []))} sections")
    logger.debug(f"Found {len(responses)} responses to analyze")
    
    recommendation_context = {}
    
    for s_idx, section in enumerate(questionnaire.get("sections", [])):
        section_name = section.get("name", f"Section {s_idx+1}")
        section_contexts = []
        
        for q_idx, question in enumerate(section.get("questions", [])):
            key = f"s{s_idx}_q{q_idx}"
            if key not in responses:
                continue
                
            response = responses[key]
            if not response:  # Skip None or empty responses
                continue
                
            # Ensure question is in dict format
            if not isinstance(question, dict):
                continue
                
            # Get recommendations for this response
            recommendations = []
            if "recommendations" in question:
                if response in question["recommendations"]:
                    # Direct match
                    recommendations.append(question["recommendations"][response])
                else:
                    # Try partial matches
                    for rec_key, rec_value in question["recommendations"].items():
                        clean_response = response.lower().strip()
                        clean_key = rec_key.lower().strip()
                        
                        if clean_key in clean_response or clean_response in clean_key:
                            recommendations.append(rec_value)
            
            if recommendations:
                q_text = question.get("text", f"Question {q_idx+1}")
                # Truncate question text if too long
                if len(q_text) > 100:
                    q_text = q_text[:97] + "..."
                    
                for rec in recommendations:
                    section_contexts.append({
                        "question_id": question.get("id", q_idx+1),
                        "question_text": q_text,
                        "response": response,
                        "recommendation": rec
                    })
        
        if section_contexts:
            recommendation_context[section_name] = section_contexts
    
    return recommendation_context

def organize_recommendations_by_priority(results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Organize recommendations by priority level
    
    Args:
        results: Assessment results dictionary
        
    Returns:
        Dictionary with high, medium, and low priority recommendation lists
    """
    logger.info("Organizing recommendations by priority")
    logger.debug(f"Processing results with {len(results.get('section_scores', {}))} sections")
    
    organized = {
        'high': [],
        'medium': [],
        'low': []
    }
    
    for section, score in results["section_scores"].items():
        if score is None:
            continue
        
        priority = get_recommendation_priority(score)
        recommendations = results["recommendations"].get(section, [])
        
        if not recommendations:
            continue
        
        section_item = {
            "section": section,
            "score": score * 100,
            "recommendations": recommendations
        }
        
        organized[priority].append(section_item)
        
    return organized
