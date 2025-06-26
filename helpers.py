""" Helper functions for the Compliance Assessment Tool.
This module contains utility functions and token management.
"""

import secrets
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import json
import logging
from datetime import datetime, timedelta
import os
import csv
from assessment import get_questionnaire, calculate_compliance_score  # Import directly from assessment
import config
from data_storage import save_assessment_data
from utils import get_regulation_and_industry_for_loader

# Import token functions directly from token_storage to avoid duplication
from token_storage import (
    ensure_token_storage,
    validate_token as ts_validate_token,
    get_organization_for_token,
    TOKENS_FILE as TOKEN_PATH,  # Use TOKENS_FILE instead of TOKEN_PATH
    generate_token as ts_generate_token,  # Changed from add_token to generate_token
    cleanup_expired_tokens as ts_cleanup_expired_tokens
)
import traceback  # Add this import at the top of the file

# Setup logging
logger = logging.getLogger(__name__)

# Session state management
def initialize_session_state():
    """Initialize all session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'welcome'
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'organization_name' not in st.session_state:
        st.session_state.organization_name = ""
    if 'selected_regulation' not in st.session_state:
        st.session_state.selected_regulation = "DPDP"
    if 'selected_industry' not in st.session_state:
        st.session_state.selected_industry = "general"
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'assessment_ready' not in st.session_state:
        st.session_state.assessment_ready = False
    if 'assessment_started' not in st.session_state:
        st.session_state.assessment_started = False
        
    # Remove assessment tab if the user navigates to Home and has not filled in details
    if st.session_state.current_page == 'welcome':
        # Reset status flag used for navigation
        st.session_state.assessment_ready = False

# Navigation functions
def go_to_page(page):
    """Navigate to a specific page in the application"""
    previous_page = st.session_state.current_page
    st.session_state.current_page = page
    logger.info(f"Navigating to page: {page} from {previous_page}")
    
    # Use rerun only if called from a button handler (not during app initialization)
    if previous_page != page:
        st.rerun()

def go_to_section(section_idx):
    """Navigate to a specific section in the assessment"""
    # Add debug logging
    logger.info(f"🔍 go_to_section called with section_idx={section_idx}")
    logger.info(f"🔍 Session state values: regulation={st.session_state.get('selected_regulation')}, industry={st.session_state.get('selected_industry')}, country={st.session_state.get('selected_country')}")
    
    # Get questionnaire for selected regulation and industry
    questionnaire = get_questionnaire(
        st.session_state.selected_regulation,
        st.session_state.selected_industry
    )
    sections = questionnaire["sections"]
    
    logger.info(f"🔍 Loaded questionnaire has {len(sections)} sections")
    if sections:
        logger.info(f"🔍 First few section names: {[s.get('name', 'Unnamed') for s in sections[:3]]}")
    
    if section_idx < 0:
        section_idx = 0
    
    if section_idx >= len(sections):
        # Completed all sections
        logger.info("Assessment completed, calculating results")
        st.session_state.assessment_complete = True
        
        # Use the correct regulation and industry mapping for calculation
        if st.session_state.selected_country == "Qatar" and st.session_state.selected_industry == "General":
            regulation_for_calc = "NPC"
            industry_for_calc = "General"
            logger.info(f"🔍 Using Qatar+General mapping: regulation_for_calc={regulation_for_calc}, industry_for_calc={industry_for_calc}")
        else:
            regulation_map = {
                "Qatar": "PDPPL",
                "India": "DPDP",
                "Australia": "OAIC"
            }
            regulation_for_calc = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
            
            # Map display industry to file industry
            industry_file_map = {
                "Oil and Gas": "Oil_and_Gas",
                "Banking and finance": "Banking and finance",
                "E-commerce": "E-commerce",
                "General": "General"
            }
            industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
            logger.info(f"🔍 Using standard mapping: regulation_for_calc={regulation_for_calc}, industry_for_calc={industry_for_calc}")
        
        logger.info(f"🔍 About to call calculate_compliance_score({regulation_for_calc}, {industry_for_calc})")
        st.session_state.results = calculate_compliance_score(
            regulation_for_calc,
            industry_for_calc
        )
        
        # Ensure organization name is set (use default if empty)
        if not st.session_state.organization_name or st.session_state.organization_name.strip() == "":
            st.session_state.organization_name = "Unnamed Organization"
        
        # Save assessment data
        assessment_data = {
            'organization_name': st.session_state.organization_name,
            'assessment_date': st.session_state.assessment_date,
            'selected_regulation': st.session_state.selected_regulation,
            'selected_industry': st.session_state.selected_industry,
            'responses': st.session_state.responses,
            'results': st.session_state.results,
            'assessment_complete': True,
            'is_complete': True  # Add this flag to trigger completion notification
        }
        save_assessment_data(assessment_data)
        
        st.session_state.current_page = 'report'
        st.rerun()  # Add explicit rerun
        return
    
    # Set flag to ensure scroll to top happens on next render
    st.session_state.scroll_to_top = True
    st.session_state.current_section = section_idx
    st.session_state.current_page = 'assessment'
    logger.info(f"Navigating to section {section_idx + 1} of {len(sections)}")
    st.rerun()  # Add explicit rerun to avoid double-click issue

# Assessment functions
def save_response(section_idx, question_idx, response):
    """Save a response to a question in the session state and persist to storage
    
    Args:
        section_idx: Index of the current section
        question_idx: Index of the question within the section
        response: The response value to save
    """
    # Skip saving if response is None
    if response is None:
        logger.warning(f"Attempted to save None response for s{section_idx}_q{question_idx}")
        return
        
    key = f"s{section_idx}_q{question_idx}"
    
    # Direct assignment is more efficient than checking previous value
    st.session_state.responses[key] = response
    logger.info(f"Saved response for {key}: '{response}'")
    
    # Save to storage if organization name exists
    if hasattr(st.session_state, 'organization_name') and st.session_state.organization_name:
        from data_storage import save_assessment_data
        assessment_data = {
            'organization_name': st.session_state.organization_name,
            'assessment_date': st.session_state.assessment_date,
            'selected_regulation': st.session_state.selected_regulation,
            'selected_industry': st.session_state.selected_industry,
            'responses': st.session_state.responses,
            'assessment_complete': st.session_state.assessment_complete
        }
        save_assessment_data(assessment_data)

def reset_assessment():
    """Reset the assessment to start over"""
    st.session_state.responses = {}
    st.session_state.assessment_complete = False
    st.session_state.results = None
    st.session_state.current_section = 0
    logger.info("Assessment reset")

def get_progress_percentage():
    """Calculate progress percentage through the assessment"""
    regulation, industry = get_regulation_and_industry_for_loader()
    questionnaire = get_questionnaire(regulation, industry)
    sections = questionnaire["sections"]
    total_questions = sum(len(section["questions"]) for section in sections)
    answered_questions = len(st.session_state.responses)
    if total_questions == 0:
        return 0
    return min(100, (answered_questions / total_questions) * 100)

def get_section_progress_percentage():
    """Calculate progress percentage through the current section"""
    regulation, industry = get_regulation_and_industry_for_loader()
    questionnaire = get_questionnaire(regulation, industry)
    sections = questionnaire["sections"]
    if st.session_state.current_section >= len(sections):
        return 100
    current_section = sections[st.session_state.current_section]
    total_questions = len(current_section["questions"])
    answered_questions = 0
    for q_idx in range(total_questions):
        key = f"s{st.session_state.current_section}_q{q_idx}"
        if key in st.session_state.responses:
            answered_questions += 1
    if total_questions == 0:
        return 0
    progress = (answered_questions / total_questions) * 100
    return min(progress, 100.0)  # Ensure never exceeds 100%

def change_questionnaire(regulation, industry):
    """Change the selected regulation and industry"""
    # Check if actually changing
    if regulation != st.session_state.selected_regulation or industry != st.session_state.selected_industry:
        logger.info(f"Changing questionnaire from {st.session_state.selected_regulation}/{st.session_state.selected_industry} to {regulation}/{industry}")
        
        # Special handling for "new banking fin" to ensure consistent naming
        if industry.lower() in ['new', 'new banking fin']:
            industry = "new banking fin"
            logger.info(f"Standardized industry name to 'new banking fin'")
        
        st.session_state.selected_regulation = regulation
        st.session_state.selected_industry = industry
        
        # Clear questionnaire cache when changing
        clear_questionnaire_cache()
        
        # Reset responses when changing questionnaire
        reset_assessment()
        logger.info(f"Changed questionnaire to {regulation}/{industry}")

def format_regulation_name(regulation: str) -> str:
    """Format regulation name for display"""
    regulation_names = {
        "DPDP": "DPDP Act",
        "PDPPL": "Qatar PDPPL",
        "NPC": "Qatar NDP",
        "QPDPPL": "Qatar PDPPL"
    }
    return regulation_names.get(regulation, regulation)

def generate_excel_download_link(results, organization, date, regulation, industry):
    """Generate a download link for Excel export of results"""
    # Create sections dataframe for Excel export of results
    sections_df = pd.DataFrame([
        {
            "Section": section, 
            "Score": score * 100,
            "Status": "High Risk" if score < 0.6 else ("Moderate Risk" if score < 0.75 else "Compliant")
        }
        for section, score in results["section_scores"].items()
        if score is not None
    ])
    
    # Get industry display name using config.get_available_industries
    available_industries = config.get_available_industries(regulation)
    industry_display_name = available_industries.get(industry, industry)
    
    # Add metadata
    metadata_df = pd.DataFrame([
        {"Key": "Organization", "Value": organization},
        {"Key": "Date", "Value": date},
        {"Key": "Regulation", "Value": config.REGULATIONS.get(regulation, regulation)},
        {"Key": "Industry", "Value": industry_display_name},
        {"Key": "Overall Score", "Value": f"{results['overall_score']:.1f}%"},
        {"Key": "Compliance Level", "Value": results['compliance_level']}
    ])
    
    # Create recommendations dataframe
    recs = []
    for section, recommendations_list in results["recommendations"].items():
        for rec in recommendations_list:
            recs.append({"Section": section, "Recommendation": rec})
    recommendations_df = pd.DataFrame(recs) if recs else pd.DataFrame(columns=["Section", "Recommendation"])
    
    # Generate Excel file with multiple sheets
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        metadata_df.to_excel(writer, sheet_name='Overview', index=False)
        sections_df.to_excel(writer, sheet_name='Section Scores', index=False)
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
    buffer.seek(0)
    
    # Create download link
    b64 = base64.b64encode(buffer.read()).decode()
    filename = f"{regulation}_{industry}_{organization.replace(' ', '_')}_{date}.xlsx"
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">[Admin] Download Excel Report</a>'

# Analytics and tracking
def track_event(event_name, properties=None):
    """Track user events for analytics"""
    try:
        # In a real implementation, this would send data to an analytics service
        # For now, we just log the event
        if properties:
            logger.info(f"EVENT: {event_name} - {json.dumps(properties)}")
        else:
            logger.info(f"EVENT: {event_name}")
        return True
    except Exception as e:
        logger.error(f"Error tracking event {event_name}: {e}")
        return False

# Token management functions - uses token_storage.py functions
def validate_token(input_token):
    """Validate if the input token exists and active"""
    # Check for admin access token first
    if input_token == 'dpdp2025':
        st.session_state.is_admin = True
        logger.info("Admin token validated")
        return True
    
    # Reset admin status for non-admin tokens
    st.session_state.is_admin = False
    
    # For debugging - note that we're attempting validation
    logger.info(f"Attempting to validate token: {input_token[:8] if input_token else 'None'}...")
    
    # Call the token_storage validation function
    is_valid = ts_validate_token(input_token)
    
    # Set organization name if token is valid
    if is_valid:
        organization = get_organization_for_token(input_token)
        if organization:
            st.session_state.organization_name = organization
        logger.info(f"Token validation successful for organization: {organization}")
    else:
        logger.warning("Token validation failed")
    
    return is_valid

def add_token(organization_name, expires_days=365, generated_by="System"):
    """Add a new token for an organization"""
    return ts_generate_token(organization_name, generated_by)  # Changed from ts_add_token to ts_generate_token

def fix_null_responses(replace_with="Not applicable"):
    """Fix null responses in session state
    
    Parameters:
    replace_with (str): Value to replace None responses with. 
                        Default is "Not applicable"
    
    Returns:
    int: Number of fixed responses
    """
    if 'responses' not in st.session_state:
        logger.warning("No responses found in session state")
        return 0
    
    responses = st.session_state.responses
    null_keys = [key for key, value in responses.items() if value is None]
    
    if not null_keys:
        logger.info("No null responses found in session state")
        return 0
    
    logger.warning(f"Found {len(null_keys)} null responses in session state: {null_keys}")
    fixed_count = 0
    
    for key in null_keys:
        st.session_state.responses[key] = replace_with
        fixed_count += 1
        logger.info(f"Fixed null response for {key}: replaced with '{replace_with}'")
    
    # Log the changes
    logger.info(f"Fixed {fixed_count} null responses")
    
    # Create backup of original responses if fixed any
    if fixed_count > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = os.path.join(backup_dir, f"responses_backup_{timestamp}.json")
        
        try:
            with open(backup_filename, 'w') as f:
                json.dump({
                    "timestamp": timestamp,
                    "fixed_responses": {k: str(v) for k, v in st.session_state.responses.items()},
                }, f, indent=2)
            logger.info(f"Backup of responses saved to {backup_filename}")
        except Exception as e:
            logger.error(f"Error saving backup: {e}")
    
    return fixed_count

def cleanup_expired_tokens() -> int:
    """Remove expired tokens from storage"""
    return ts_cleanup_expired_tokens()

def debug_questionnaire_structure(questionnaire):
    """Debug function to log the structure of a questionnaire"""
    try:
        logger.info("Debugging questionnaire structure")
        logger.info(f"Questionnaire keys: {list(questionnaire.keys())}")
        if "sections" not in questionnaire:
            logger.error("Questionnaire has no 'sections' key")
            return
        sections = questionnaire["sections"]
        logger.info(f"Number of sections: {len(sections)}")
        for i, section in enumerate(sections):
            logger.info(f"Section {i}: {section.get('name', 'Unnamed')} with {len(section.get('questions', []))} questions")
            # Check question formats
            for j, question in enumerate(section.get("questions", [])):
                if isinstance(question, dict):
                    logger.info(f"  Question {j}: Dictionary format, keys: {list(question.keys())}")
                else:
                    logger.info(f"  Question {j}: String format: {question[:30]}...")
        logger.info("End of questionnaire structure debug")
    except Exception as e:
        logger.error(f"Error debugging questionnaire structure: {e}")

def fix_questionnaire_selection():
    """Fix a mismatch between selected industry and actual questionnaire file"""
    try:
        # Check if the questionnaire needs fixing
        if ('current_questionnaire' in st.session_state and 
            'sections' in st.session_state.current_questionnaire and
            'selected_industry' in st.session_state):
            
            # Log full details about current questionnaire
            section_count = len(st.session_state.current_questionnaire.get('sections', []))
            logger.info(f"CHECKING questionnaire: industry={st.session_state.selected_industry}, sections={section_count}")
            logger.info(f"Section names: {[s.get('name', 'Unnamed') for s in st.session_state.current_questionnaire.get('sections', [])]}")
            
            # CRITICAL: Check if we have a locked questionnaire type
            if hasattr(st.session_state, 'locked_questionnaire_type'):
                if (st.session_state.locked_questionnaire_type == "e-commerce" and 
                    (st.session_state.selected_industry != "e-commerce" or section_count < 4)):
                    logger.warning(f"Detected violation of locked E-commerce questionnaire - forcing reload")
                    # Clear the cache to force reload
                    if 'current_questionnaire' in st.session_state:
                        del st.session_state.current_questionnaire
                    st.session_state.selected_industry = "e-commerce"
                    st.session_state.clear_questionnaire_cache = True
                    logger.info(f"Force-reset industry to e-commerce from locked context")
                    return True
            
            # Get the expected section count based on industry
            expected_section_count = 4 if st.session_state.selected_industry.lower() == "e-commerce" else 2
            
            # CRITICAL FIX: Detect if we have fewer sections than expected for E-commerce
            if (st.session_state.selected_industry.lower() == "e-commerce" and 
                section_count < 4):
                
                logger.warning(f"DETECTED INCORRECT QUESTIONNAIRE: E-commerce selected but only has {section_count} sections instead of 4")
                logger.warning(f"Stack trace:\n{''.join(traceback.format_stack()[-8:-1])}")
                
                # Clear the questionnaire cache to force reload
                if 'current_questionnaire' in st.session_state:
                    del st.session_state.current_questionnaire
                
                # Signal to clear the cache in assessment module
                st.session_state.clear_questionnaire_cache = True
                # Lock the questionnaire type to prevent further switches
                st.session_state.locked_questionnaire_type = "e-commerce"
                st.session_state.locked_section_count = 4
                logger.info("LOCKED questionnaire type to e-commerce and cleared cache")
                return True
            
            # ...existing code for other checks...
                
        return False
            
    except Exception as e:
        logger.error(f"Error fixing questionnaire selection: {e}", exc_info=True)
        return False

def clear_questionnaire_cache():
    """Clear the questionnaire cache to force reload on next access"""
    st.session_state.clear_questionnaire_cache = True
    logger.info("Questionnaire cache will be cleared on next access")
    
    # ADDITIONAL DEBUGGING: Track where this is being called from
    logger.info(f"Cache clearing requested from:\n{''.join(traceback.format_stack()[-5:-1])}")
    
    # Also clear the current_questionnaire in session_state if it exists
    if 'current_questionnaire' in st.session_state:
        del st.session_state.current_questionnaire
        logger.info("Current questionnaire cleared from session state")
