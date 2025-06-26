"""
Questionnaire Loader Module for the Compliance Assessment Tool.

This module handles:
- Loading and validating questionnaires from files
- Providing helper functions to access questionnaire sections and questions
- Converting legacy questionnaire formats to the new structure
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from config import BASE_DIR, QUESTIONNAIRE_DIR

# Setup logging
logger = logging.getLogger(__name__)

def load_questionnaire(regulation: str, industry: str) -> dict:
    """Load questionnaire from file with more robust path handling"""
    # Clean input to prevent path traversal
    regulation = ''.join(c for c in regulation if c.isalnum())
    industry = ''.join(c for c in industry if c.isalnum())
    
    # Construct path relative to questionnaire directory
    file_path = os.path.join(QUESTIONNAIRE_DIR, regulation, f"{industry}.json")
    
    # Verify the path is still within QUESTIONNAIRE_DIR
    if not os.path.abspath(file_path).startswith(os.path.abspath(QUESTIONNAIRE_DIR)):
        raise ValueError("Invalid questionnaire path")

    try:
        # Use less verbose logging
        logger.debug(f"Attempting to load questionnaire from {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"Questionnaire file not found: {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            questionnaire = json.load(f)
            
        # Validate questionnaire structure
        if validate_questionnaire_structure(questionnaire):
            logger.debug(f"Successfully loaded questionnaire from {file_path}")
            return questionnaire
        else:
            logger.error(f"Invalid questionnaire structure in {file_path}")
            # Try to fix the questionnaire structure
            fixed_questionnaire = fix_questionnaire_weights(questionnaire)
            if fixed_questionnaire:
                logger.info(f"Fixed questionnaire weights for {file_path}")
                return fixed_questionnaire
        
            
    except Exception as e:
        logger.error(f"Error loading questionnaire: {e}")
        return {}

def validate_questionnaire_structure(questionnaire: Dict[str, Any]) -> bool:
    """Validate the structure of a questionnaire"""
    try:
        # Check required top-level keys
        required_keys = ["sections"]
        if not all(key in questionnaire for key in required_keys):
            logger.error(f"Missing required keys in questionnaire: {required_keys}")
            return False
            
        # Validate sections
        sections = questionnaire["sections"]
        if not isinstance(sections, list) or not sections:
            logger.error(f"Questionnaire sections must be a non-empty list. Got {type(sections)} with {len(sections) if isinstance(sections, list) else 0} items")
            return False
            
        # Validate each section
        total_weight = 0
        for idx, section in enumerate(sections):
            # Check required section keys
            required_section_keys = ["name", "weight", "questions"]
            if not all(key in section for key in required_section_keys):
                missing = [key for key in required_section_keys if key not in section]
                logger.error(f"Section {idx} missing required keys: {missing}")
                return False
                
            # Validate weight
            if not isinstance(section["weight"], (int, float)) or section["weight"] <= 0:
                logger.error(f"Section {idx} weight must be a positive number. Got {section['weight']}")
                return False
            total_weight += section["weight"]
            
            # Check if questions have required properties
            questions = section["questions"]
            for q_idx, question in enumerate(questions):
                if isinstance(question, dict):
                    # New format with detailed question structure
                    required_question_keys = ["id", "text", "options"]
                    if not all(key in question for key in required_question_keys):
                        missing = [key for key in required_question_keys if key not in question]
                        logger.error(f"Section {idx}, question {q_idx} missing required keys: {missing}")
                        return False
                # If question is a string, it's the old format, which is still valid
        
        # More flexible check for weight totals (0.98-1.02)
        if not 0.98 <= total_weight <= 1.02:
            logger.warning(f"Total section weights ({total_weight}) not close to 1.0 - this may affect scoring accuracy")
            weights = [f"{section['name']}: {section['weight']}" for section in sections]
            logger.warning(f"Individual weights: {', '.join(weights)}")
            # Return True anyway - we'll normalize the weights during scoring
            return True
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating questionnaire: {e}")
        return False

def fix_questionnaire_weights(questionnaire: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Attempt to fix questionnaire weights to sum to 1.0"""
    try:
        if "sections" not in questionnaire or not questionnaire["sections"]:
            return None
        
        sections = questionnaire["sections"]
        section_count = len(sections)
        if section_count == 0:
            return None
        
        # Set equal weights for all sections
        for section in sections:
            if "weight" not in section or not isinstance(section["weight"], (int, float)) or section["weight"] <= 0:
                section["weight"] = 1.0 / section_count
            
        # Calculate total weight
        total_weight = sum(section["weight"] for section in sections)
        
        # If total weight is close to 1.0, no adjustment needed
        if 0.99 <= total_weight <= 1.01:
            return questionnaire
        
        # Otherwise, normalize weights
        for section in sections:
            section["weight"] = section["weight"] / total_weight
        
        logger.info(f"Fixed questionnaire weights. Original total: {total_weight}, new total: {sum(section['weight'] for section in sections)}")
        return questionnaire
    except Exception as e:
        logger.error(f"Error fixing questionnaire weights: {e}")
        return None

# The following functions are likely unused in the main application flow:
def get_section_count(questionnaire: Dict[str, Any]) -> int:
    """Get the number of sections in a questionnaire"""
    # This functionality can be achieved with len(questionnaire.get("sections", []))
    return len(questionnaire.get("sections", []))

def get_section_questions(questionnaire: Dict[str, Any], section_index: int) -> List[Any]:
    """Get questions for a specific section"""
    # This can be done with direct access: questionnaire["sections"][section_index]["questions"]
    try:
        return questionnaire["sections"][section_index]["questions"]
    except (KeyError, IndexError):
        return []

def get_section_options(questionnaire: Dict[str, Any], section_index: int, question_index: int = None) -> List[Any]:
    """Get answer options for a specific question"""
    # Complex accessor that could be inlined where needed
    # ...existing code...

def get_section_weight(questionnaire: Dict[str, Any], section_index: int) -> float:
    """Get the weight for a specific section"""
    # Simple accessor that could be inlined
    try:
        return questionnaire["sections"][section_index]["weight"]
    except (KeyError, IndexError):
        return 0.0

def get_default_questionnaire() -> Dict[str, Any]:
    """Get the default questionnaire structure"""
    # Could be replaced with inline dictionary where needed
    # ...existing code...
