"""User interface rendering functions for the Compliance Assessment Tool.
This module contains all the Streamlit UI components and page rendering.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import os
import time
import base64
from typing import Dict, List, Any, Optional, Tuple  # Add typing imports
import tempfile
import re
from markdown_pdf import MarkdownPdf, Section # Add markdown-pdf imports
import config
# Update import: get reg/ind functions from config instead of assessment
from config import get_available_regulations, get_available_industries
from assessment import get_questionnaire, calculate_compliance_score
# Import from new recommendation engine instead of assessment
from recommendation_engine import get_recommendation_priority, organize_recommendations_by_priority
from helpers import (
    go_to_page, 
    save_response, 
    generate_excel_download_link,
    get_section_progress_percentage,  # Use this instead of local implementation
    format_regulation_name,
    validate_token
)
from token_storage import generate_token, cleanup_expired_tokens, revoke_token, get_organization_for_token, TOKENS_FILE
from utils import get_regulation_and_industry_for_loader
# Import the newly created styles
from styles import (
    get_landing_page_css, 
    get_expiry_box_css,
    get_section_navigation_css,
    get_common_button_css,
    get_penalties_table_css,
    get_discovery_button_css,
    get_faq_css,
    get_input_label_css,
    get_contact_link_css,
    get_ai_analysis_css,
    get_penalties_section_css,
    get_countdown_section_css,
    get_logo_css,
    get_data_discovery_css,
    get_penalties_note_css,
    get_ai_report_css,
    get_download_button_css
)

from faq import FAQ_DATA  # Add this import at the top

# Add import at the top with other imports

# Setup logging
logger = logging.getLogger(__name__)

# Ensure assessment_type is initialized in session state
if 'assessment_type' not in st.session_state:
    st.session_state.assessment_type = 'PDPPL'

def render_header():
    """Render the application header"""
    org_name = st.session_state.organization_name if st.session_state.organization_name and st.session_state.organization_name.strip() else None
    
    st.markdown("""
        <style>
        /* Compact header */
        .app-header {
            background: rgba(30, 30, 30, 0.8);
            padding: 0.4rem 0.5rem;
            border-radius: 4px;
            margin: 0;
        }
        .header-text {
            margin: 0;
            padding: 0;
            text-align: center;
        }
        .header-text h1 {
            color: white;
            font-size: 2.2rem;
            margin: 0;
            padding: 0;
            line-height: 1.1;
        }
        .header-text p {
            color: rgba(250, 250, 250, 0.8);
            font-size: 1.15rem;
            margin: 0.1rem 0 0 0;
            padding: 0;
            line-height: 1;
        }
        /* Remove all Streamlit spacing */
        .element-container, div[data-testid="stMarkdown"], div[data-testid="stVerticalBlock"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Compact section title */
        .section-title {
            font-size: 1.2rem;
            margin: 0.3rem 0;
            padding: 0;
            line-height: 1.2;
        }
        /* Compact progress section */
        .progress-section {
            margin: 0.3rem 0;
            padding: 0;
            font-size: 0.85rem;
            opacity: 0.8;
        }
        .stProgress {
            margin: 0.2rem 0 !important;
            padding: 0 !important;
        }
        /* Question spacing */
        .question-container {
            margin-top: 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Minimal HTML structure
    header_html = (
        '<div class="app-header">'
        '<div class="header-text">'
        f'<h1>{config.APP_TITLE}</h1>'
        f'{f"<p>Organization: {org_name}</p>" if org_name else ""}'
        '</div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

# Landing page function (moved from landing.py)
def render_landing_page():
    """Render the landing page with token authentication"""
    # Add admin navigation button if user has admin privileges
    if st.session_state.get('is_admin', False):
        if st.button("Admin Dashboard", key="admin_nav"):
            st.session_state.current_page = 'admin'
            st.rerun()
            
    # Apply custom CSS
    st.markdown(get_landing_page_css(), unsafe_allow_html=True)
    st.markdown(get_contact_link_css(), unsafe_allow_html=True)
    
    # Add CSS to center the main content block and logo
    st.markdown("""
        <style>
        /* Target the main block containing landing page elements */
        div[data-testid="stVerticalBlock"] > div.stHorizontalBlock > div[data-testid="stVerticalBlock"] {
            align-items: center;
        }
        
        /* Improved logo centering */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 0 auto;
            padding: 20px 0;
        }
        
        .logo-container img {
            max-width: 300px;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        
        /* Ensure the middle column is properly centered */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

    # Logo - Display using columns and centered text within middle column
    if os.path.exists(config.LOGO_PATH):
        col1, col2, col3 = st.columns([1, 1, 1]) # Equal ratios
        with col2:
            # Use the improved CSS class for logo centering
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image(config.LOGO_PATH, width=300) # Increased width from 200 to 300
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(f"Logo not found at path: {config.LOGO_PATH}")
    
    # Title
    st.markdown(f"""
        <div class="title-container">
            <h1>{config.APP_TITLE}</h1>
            <p>Enter your access token to begin the assessment</p>
            <p class="contact-link">If you do not have a token, please <a href="mailto:info@datainfa.com?subject=Requesting%20Access%20token%20for%20my%20organisation">contact us</a> to get your access token.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Token input with centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        token = st.text_input("Access Token", type="password")
        if st.button("Access Assessment", type="primary", use_container_width=True):
            if validate_token(token):
                st.session_state.authenticated = True
                st.session_state.current_page = 'welcome'
                st.rerun()
            else:
                st.error("Invalid token. Please try again or contact support.")
    
    # Footer
    st.markdown("""
        <div class="footer">
            &copy; 2025 Compliance Assessment Tool | All Rights Reserved
        </div>
    """, unsafe_allow_html=True)

def render_assessment():
    """Render the assessment page"""
    # Get current regulation and industry
    current_regulation = st.session_state.get('regulation', 'PDPPL')
    current_industry = st.session_state.get('industry', 'General')
    
    # Initialize session state for responses if not exists
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    # Get questionnaire for current regulation and industry
    questionnaire = get_questionnaire(current_regulation, current_industry)
    sections = questionnaire.get('sections', [])
    
    # Track current section
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    
    # Only recalculate if:
    # 1. We have responses
    # 2. The regulation or industry has changed
    # 3. We haven't calculated for this combination before
    cache_key = f"score_cache_{current_regulation}_{current_industry}"
    if (st.session_state.responses and 
        (not hasattr(st.session_state, cache_key) or 
         st.session_state.get('last_regulation') != current_regulation or
         st.session_state.get('last_industry') != current_industry)):
        
        # Update last used regulation and industry
        st.session_state.last_regulation = current_regulation
        st.session_state.last_industry = current_industry
        
        # Calculate compliance score
        results = calculate_compliance_score(current_regulation, current_industry)
        st.session_state.assessment_results = results
    elif hasattr(st.session_state, 'assessment_results'):
        results = st.session_state.assessment_results
    else:
        results = None
    
    # Create a top anchor without extra spacing
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    
    # Check if questionnaire needs to be reloaded due to country/industry change
    need_reload = False
    if 'current_questionnaire' not in st.session_state:
        need_reload = True
    else:
        # Check if country or industry has changed
        cached_country = st.session_state.get('cached_country')
        cached_industry = st.session_state.get('cached_industry')
        current_country = st.session_state.get('selected_country')
        current_industry = st.session_state.get('selected_industry')
        
        if cached_country != current_country or cached_industry != current_industry:
            logger.info(f"Country/Industry changed: {cached_country}/{cached_industry} -> {current_country}/{current_industry}")
            need_reload = True
            # Clear the questionnaire cache
            from helpers import clear_questionnaire_cache
            clear_questionnaire_cache()
    
    # Get questionnaire data
    if need_reload:    
        # Add debug logs for session state
        logger.info(f"[render_assessment] Session selected_country: {st.session_state.get('selected_country')}")
        logger.info(f"[render_assessment] Session selected_industry: {st.session_state.get('selected_industry')}")
        # Map display industry to file industry
        industry_file_map = {
            "Oil and Gas": "Oil_and_Gas",
            "Banking and finance": "Banking and finance",
            "E-commerce": "E-commerce"
        }
        industry_for_loader = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
        logger.info(f"[render_assessment] Mapped industry_for_loader: {industry_for_loader}")
        # Map country to regulation code
        regulation_map = {
            "Qatar": "PDPPL",
            "India": "DPDP",
            "Australia": "OAIC",
            "Saudi Arabia": "PDPL"
        }
        
        # Use the proper regulation based on country selection
        if st.session_state.selected_country == "Qatar" and st.session_state.selected_industry == "General":
            regulation_for_loader = "NPC"
            logger.info(f"[render_assessment] Using NPC for Qatar General industry")
        else:
            regulation_map = {
                "Qatar": "PDPPL",
                "India": "DPDP",
                "Australia": "OAIC",
                "Saudi Arabia": "PDPL"
            }
            regulation_for_loader = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
            logger.info(f"[render_assessment] Using regulation: {regulation_for_loader} for country: {st.session_state.selected_country}")
        try:
            questionnaire = get_questionnaire(regulation_for_loader, industry_for_loader)
            logger.info(f"[render_assessment] Loaded questionnaire for regulation: {regulation_for_loader}, industry: {industry_for_loader}")
        except Exception as e:
            logger.error(f"[render_assessment] Error loading questionnaire for regulation: {regulation_for_loader}, industry: {industry_for_loader}: {e}")
            raise
        st.session_state.current_questionnaire = questionnaire
        # Cache the current country/industry to detect changes
        st.session_state.cached_country = st.session_state.get('selected_country')
        st.session_state.cached_industry = st.session_state.get('selected_industry')
    questionnaire = st.session_state.current_questionnaire
    
    # Show questionnaire debug info in sidebar with more details
    with st.sidebar.expander("Navigation panel", expanded=False):
        st.markdown("""
            <style>
            div.stExpander {
                background-color: #0e1117;
                border: 1px solid rgba(49, 51, 63, 0.2);
            }
            /* Dark theme buttons */
            div.stButton > button {
                width: 100%;
                padding: 0.5rem;
                margin: 0.25rem 0;
                background-color: #1e1e1e !important;
                color: #fafafa;
                border: 1px solid #333333 !important;
                border-radius: 0.3rem;
                transition: all 0.2s;
            }
            /* Hover effect */
            div.stButton > button:hover:not(:disabled) {
                background-color: #2d2d2d !important;
                border-color: #404040 !important;
            }
            /* Disabled button */
            div.stButton > button:disabled {
                background-color: #161616 !important;
                color: #666666;
                border-color: #292929 !important;
            }
            /* Current section highlight */
            div.stButton > button.current {
                border-left: 3px solid #666666 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if "sections" in questionnaire:
            st.write("Jump to section:")
            
            # Create list of sections with completion status
            for i, section in enumerate(questionnaire["sections"]):
                section_name = section.get("name", f"Section {i+1}")
                
                # Calculate if section is complete
                questions = section.get("questions", [])
                answered = sum(1 for q_idx in range(len(questions)) 
                             if f"s{i}_q{q_idx}" in st.session_state.responses)
                complete = answered == len(questions)
                
                # Create button with status indicator
                button_label = f"{i+1}. {section_name} [{answered}/{len(questions)}]"
                if st.button(button_label, key=f"nav_section_{i}", 
                           disabled=i == st.session_state.current_section,
                           use_container_width=True):
                    st.session_state.current_section = i
                    # Only rerun if actually changing sections
                    if i != st.session_state.current_section:
                        st.rerun()
    
    # TESTING ONLY - TO BE REMOVED BEFORE PRODUCTION
    # Add quick-fill testing option in sidebar for faster testing
    if st.session_state.get('is_admin', False):
        st.markdown("""
            <style>
            /* Expander styling */
            .streamlit-expanderHeader {
                background-color: #262730 !important;
                border: none !important;
                border-radius: 4px !important;
                color: #fafafa !important;
                font-size: 14px !important;
            }
            .streamlit-expanderHeader:hover {
                background-color: #1E1E1E !important;
            }
            /* Testing tools container */
            div.stExpander {
                border: none !important;
                background-color: transparent !important;
            }
            /* Radio buttons in testing tools */
            div.stExpander div[data-testid="stRadio"] > div {
                display: flex !important;
                flex-direction: column !important;
                gap: 8px !important;
            }
            div.stExpander div[data-testid="stRadio"] label {
                background-color: #262730 !important;
                padding: 8px 12px !important;
                border-radius: 4px !important;
                color: #fafafa !important;
                transition: all 0.2s !important;
            }
            div.stExpander div[data-testid="stRadio"] label:hover {
                background-color: #1E1E1E !important;
                color: #6fa8dc !important;
            }
            /* Button styling */
            div.stExpander div[data-testid="stButton"] > button {
                width: 100% !important;
                padding: 8px 12px !important;
                margin: 4px 0 !important;
                background-color: #262730 !important;
                color: #fafafa !important;
                border: none !important;
                border-radius: 4px !important;
                text-align: left !important;
                transition: all 0.2s !important;
            }
            div.stExpander div[data-testid="stButton"] > button:hover {
                background-color: #1E1E1E !important;
                color: #6fa8dc !important;
            }
            div.stExpander div[data-testid="stButton"] > button:active {
                border-left: 3px solid #6fa8dc !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.sidebar.expander("TESTING TOOLS", expanded=True):
            auto_fill_option = st.radio(
                "Auto-fill responses with:",
                ["None", "All Yes/Positive", "All Partial/Medium", "All No/Negative", "Random Mix"],
                key="auto_fill_option",
                index=4  # Set default to "Random Mix" (index 4 in the list)
            )
            if st.button("Apply Auto-Fill", key="apply_auto_fill", type="primary"):
                sections = questionnaire["sections"]
                current_section = st.session_state.current_section
                
                if current_section < len(sections):
                    section = sections[current_section]
                    questions = section.get("questions", [])
                    
                    import random
                    responses_updated = False
                
                    for q_idx, question in enumerate(questions):
                        # Create the response key in the correct format
                        response_key = f"s{current_section}_q{q_idx}"
                        radio_key = f"radio_{response_key}"
                        
                        # Get options for the question
                        if isinstance(question, dict):
                            options = question.get("options", [])
                        else:
                            try:
                                options = section.get("options", [])[q_idx]
                            except (IndexError, KeyError):
                                options = ["Yes", "No", "Not applicable"]
                        
                        # Select option based on auto-fill choice
                        selected_option = None
                        if auto_fill_option == "All Yes/Positive":
                            selected_option = options[0]  # First option (Yes/Positive)
                        elif auto_fill_option == "All Partial/Medium":
                            selected_option = options[1] if len(options) > 2 else options[0]  # Middle option if available
                        elif auto_fill_option == "All No/Negative":
                            selected_option = options[-1]  # Last option (No/Negative)
                        elif auto_fill_option == "Random Mix":
                            selected_option = random.choice(options)  # Random choice
                        
                        # Update both session state entries
                        if selected_option:
                            st.session_state.responses[response_key] = selected_option
                            st.session_state[radio_key] = selected_option
                            responses_updated = True
                    
                    if responses_updated:
                        st.sidebar.success("Responses auto-filled successfully!")
                        # Update the auto-fill state
                        st.session_state.auto_fill_complete = True
                        # Use st.rerun() as per latest Streamlit version
                        st.rerun()
                else:
                    st.error("No section available for auto-fill")
    
    # END OF TESTING CODE
    

    sections = questionnaire["sections"]
    
    # Check if questionnaire has any sections
    if not sections:
        st.error("No assessment questions found for the selected regulation and industry. Please select a different combination.")
        if st.button("Back to Welcome"):
            st.session_state.current_page = 'welcome'
            st.rerun()
        return
    
    # Debug display to show section progress
    st.sidebar.write(f"Current Section: {st.session_state.current_section + 1} of {len(sections)}")
    st.sidebar.write(f"Total Sections: {len(sections)}")
    
    if st.session_state.current_section >= len(sections):
        st.session_state.assessment_complete = True
        # Force recalculation of results using correct mapping
        if st.session_state.selected_country == "Qatar" and st.session_state.selected_industry == "General":
            regulation_for_calc = "NPC"
        else:
            regulation_map = {
                "Qatar": "PDPPL",
                "India": "DPDP",
                "Australia": "OAIC",
                "Saudi Arabia": "PDPL"
            }
            regulation_for_calc = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
        
        # Map display industry to file industry
        industry_file_map = {
            "Oil and Gas": "Oil_and_Gas",
            "Banking and finance": "Banking and finance",
            "E-commerce": "E-commerce",
            "General": "General"  # Keep General as is for NPC
        }
        industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
        
        st.session_state.results = calculate_compliance_score(
            regulation_for_calc,
            industry_for_calc
        )
        
        # Redirect to report page
        st.session_state.current_page = 'report'
        st.rerun()
        return
    
    # Get current section
    current_section = sections[st.session_state.current_section]
    section_name = current_section["name"]
    questions = current_section["questions"]
    
    # Display section name prominently
    st.markdown(f"""
        <div class="section-header">
            <h2>Part {st.session_state.current_section + 1}: {section_name}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate overall progress across all sections
    total_questions = sum(len(section["questions"]) for section in sections)
    
    # Count only responses that belong to the current questionnaire structure
    answered_questions = 0
    for s_idx, section in enumerate(sections):
        section_questions = len(section.get("questions", []))
        for q_idx in range(section_questions):
            response_key = f"s{s_idx}_q{q_idx}"
            if response_key in st.session_state.responses and st.session_state.responses[response_key] is not None:
                answered_questions += 1
    
    overall_progress = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
    # Ensure progress never exceeds 100%
    overall_progress = min(overall_progress, 100.0)
    section_progress = get_section_progress_percentage()
    
    # Show progress bar and metrics compactly
    st.progress(overall_progress / 100)
    st.markdown(f'''
        <div class="progress-section">
            <span style="float:left">Part progress: {section_progress:.1f}%</span>
            <span style="float:right">Overall progress: {overall_progress:.1f}% ({answered_questions}/{total_questions} questions)</span>
            <div style="clear:both"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Create form for questions
    with st.form(key=f"section_form_{st.session_state.current_section}"):
        # Display questions
        for q_idx, question in enumerate(current_section["questions"]):
            # Get question details
            q_id = question.get("id", q_idx + 1) if isinstance(question, dict) else q_idx + 1
            q_text = question.get("text", question) if isinstance(question, dict) else question
            options = question.get("options", []) if isinstance(question, dict) else current_section.get("options", [])[q_idx]
            
            # Render question compactly
            st.markdown(f"""
                <div class="question-container">
                    <h4>Question {q_id}</h4>
                    <div class="question-text">{q_text}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Create response radio buttons
            response_key = f"s{st.session_state.current_section}_q{q_idx}"
            radio_key = f"radio_{response_key}"
            current_response = st.session_state.responses.get(response_key)
            
            # Determine index for radio button - None for no pre-selection, or index of saved response
            radio_index = None
            if current_response and current_response in options:
                radio_index = options.index(current_response)
            
            response = st.radio(
                "Select your response:",
                options,
                key=radio_key,
                index=radio_index
            )
            
            # Only save response if user actually made a selection (response is not None)
            if response is not None and response != current_response:
                save_response(st.session_state.current_section, q_idx, response)
                st.session_state.responses[response_key] = response
        
        # Navigation buttons
        st.markdown(get_common_button_css(), unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.current_section > 0:
                prev_clicked = st.form_submit_button("Previous Section")
                if prev_clicked:
                    st.session_state.current_section -= 1
                    # Only rerun if actually changing sections
                    if st.session_state.current_section >= 0:
                        st.rerun()
        
        with col2:
            is_last_section = st.session_state.current_section == len(questionnaire["sections"]) - 1
            next_label = "Complete Assessment" if is_last_section else "Next Section"
            next_clicked = st.form_submit_button(next_label)
            if next_clicked:
                # Validate responses - check for missing or None responses
                unanswered = []
                for q_idx in range(len(current_section["questions"])):
                    response_key = f"s{st.session_state.current_section}_q{q_idx}"
                    response = st.session_state.responses.get(response_key)
                    if response is None:  # Either missing or explicitly None from radio button
                        unanswered.append(q_idx + 1)
                
                if not unanswered:
                    if is_last_section:
                        st.session_state.assessment_complete = True
                        # Force recalculation of results using correct mapping
                        if st.session_state.selected_country == "Qatar" and st.session_state.selected_industry == "General":
                            regulation_for_calc = "NPC"
                        else:
                            regulation_map = {
                                "Qatar": "PDPPL",
                                "India": "DPDP",
                                "Australia": "OAIC",
                                "Saudi Arabia": "PDPL"
                            }
                            regulation_for_calc = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
                        
                        # Map display industry to file industry
                        industry_file_map = {
                            "Oil and Gas": "Oil_and_Gas",
                            "Banking and finance": "Banking and finance",
                            "E-commerce": "E-commerce",
                            "General": "General"  # Keep General as is for NPC
                        }
                        industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
                        
                        st.session_state.results = calculate_compliance_score(
                            regulation_for_calc,
                            industry_for_calc
                        )
                        
                        # Redirect to report page
                        st.session_state.current_page = 'report'
                        st.rerun()
                    else:
                        st.session_state.current_section += 1
                        # Only rerun if actually changing sections
                        if st.session_state.current_section < len(questionnaire["sections"]):
                            st.rerun()
                else:
                    st.error(f"Please answer question(s) {', '.join(map(str, unanswered))} before proceeding.")


from nlg_report import generate_report

def generate_natural_language_report(results: Dict[str, Any]) -> str:
    """
    Generate human-readable report using AI
    """
    logger.info("Requesting AI report generation with the following configuration:")
    logger.info(f"AI enabled: {config.get_ai_enabled()}")
    logger.info(f"API key available: {'Yes' if config.get_ai_api_key() else 'No'}")
    logger.info(f"API provider: {config.get_ai_provider()}")
    
    # Record timing information
    start_time = time.time()
    try:
        report = generate_report(results, use_external_api=config.get_ai_enabled())
        if not report:
            logger.error("Report generation failed - no content returned")
            return "Error: Failed to generate report. Please try again or contact support."
    except Exception as e:
        logger.error(f"Error in report generation: {e}")
        return "Error: Failed to generate report. Please try again or contact support."
        
    duration = time.time() - start_time
    logger.info(f"Report generation completed in {duration:.2f} seconds")
    logger.info(f"Report length: {len(report)} characters")
    
    return report

def render_report():
    """Render the compliance report"""
    if not st.session_state.assessment_complete:
        st.info("Complete the assessment to view your compliance report")
        if st.button("Go to Assessment", type="primary"):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return

    # Clear questionnaire cache to ensure we get fresh data
    if not st.session_state.get('report_cache_cleared', False):
        st.session_state.clear_questionnaire_cache = True
        st.session_state.report_cache_cleared = True
    
    results = st.session_state.results
    
    # CRITICAL FIX: Force fresh calculation if we detect stale results
    # Check if results contain wrong questionnaire type before proceeding
    if results:
        result_section_names = list(results.get("section_scores", {}).keys())
        regulation_for_loader, industry_for_loader = get_regulation_and_industry_for_loader()
        
        # If we expect NPC but results contain PDPPL sections, force recalculation
        if regulation_for_loader == "NPC" and any("PDPPL" in name or "Principles of Data Privacy" in name for name in result_section_names):
            logger.warning(f"[STALE] Detected stale PDPPL results when expecting NPC. Forcing fresh calculation...")
            st.session_state.clear_questionnaire_cache = True
            
            # Force fresh calculation with correct parameters
            regulation_map = {"Qatar": "PDPPL", "India": "DPDP", "Australia": "OAIC"}
            regulation_for_calc = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
            logger.info(f"[STALE] Recalculating with correct regulation: {regulation_for_calc}")
            
            industry_file_map = {
                "Oil and Gas": "Oil_and_Gas",
                "Banking and finance": "Banking and finance", 
                "E-commerce": "E-commerce",
                "General": "General"
            }
            industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
            
            logger.info(f"[STALE] Recalculating with fresh {regulation_for_calc}/{industry_for_calc}")
            st.session_state.results = calculate_compliance_score(regulation_for_calc, industry_for_calc)
            results = st.session_state.results
            st.info("🔄 **Refreshed stale results** - Now using correct NPC questionnaire data.")
    elif actual_section_count < expected_section_count:
        # Auto-fix section count mismatch too
        st.info(f"🔄 **Auto-processing all sections** - Ensuring all {expected_section_count} sections are included...")
        
        # DEMO MODE: Force NPC for all selections
        regulation_for_calc = "NPC"
        logger.info(f"[DEMO] AUTO-FIXING: FORCING NPC for Process All Sections")
        
        # Map display industry to file industry
        industry_file_map = {
            "Oil and Gas": "Oil_and_Gas",
            "Banking and finance": "Banking and finance",
            "E-commerce": "E-commerce",
            "General": "General"
        }
        industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
        
        st.session_state.results = calculate_compliance_score(
            regulation_for_calc,
            industry_for_calc
        )
        st.success(f"✅ **Auto-processed all {expected_section_count} sections!** Report now shows complete results.")
        st.rerun()
    
    st.subheader(f"{format_regulation_name(st.session_state.selected_regulation)}  Compliance Report")
    # st.subheader(f"For: {st.session_state.organization_name}")
    # st.write(f"Assessment Date: {st.session_state.assessment_date}")
    
    # Get questionnaire to check how many sections it has vs how many have scores
    regulation_for_loader, industry_for_loader = get_regulation_and_industry_for_loader()
    questionnaire = get_questionnaire(regulation_for_loader, industry_for_loader)
    expected_section_count = len(questionnaire.get("sections", []))
    actual_section_count = len(results.get("section_scores", {}))
    
    # Check if we have a questionnaire type mismatch (CRITICAL FIX)
    expected_section_names = [section["name"] for section in questionnaire.get("sections", [])]
    actual_section_names = list(results.get("section_scores", {}).keys())
    
    # Detect if we're using the wrong questionnaire (e.g., PDPPL sections for NPC)
    questionnaire_mismatch = False
    if regulation_for_loader == "NPC" and any("PDPPL" in name for name in actual_section_names):
        logger.warning(f"[MISMATCH] QUESTIONNAIRE MISMATCH DETECTED: Expected NPC sections but found PDPPL sections in results")
        questionnaire_mismatch = True
    elif regulation_for_loader == "PDPPL" and any("Data Management Strategy" in name for name in actual_section_names):
        logger.warning(f"[MISMATCH] QUESTIONNAIRE MISMATCH DETECTED: Expected PDPPL sections but found NPC sections in results")
        questionnaire_mismatch = True
    
    # Show questionnaire mismatch and auto-fix it immediately for demo
    if questionnaire_mismatch:
        # Prevent infinite loops with a session state flag
        if not st.session_state.get('auto_fixing_mismatch', False):
            st.session_state.auto_fixing_mismatch = True
            
            st.info(f"🔄 **Auto-fixing questionnaire mismatch** - Recalculating with correct {regulation_for_loader} questionnaire...")
            
            # Add a small delay to make the process visible
            import time
            time.sleep(1)
            
            # Use correct regulation mapping
            regulation_map = {"Qatar": "PDPPL", "India": "DPDP", "Australia": "OAIC"}
            regulation_for_calc = regulation_map.get(st.session_state.selected_country, st.session_state.selected_regulation)
            logger.info(f"[AUTO-FIX] Using correct regulation: {regulation_for_calc}")
            
            # Map display industry to file industry
            industry_file_map = {
                "Oil and Gas": "Oil_and_Gas",
                "Banking and finance": "Banking and finance",
                "E-commerce": "E-commerce",
                "General": "General"
            }
            industry_for_calc = industry_file_map.get(st.session_state.selected_industry, st.session_state.selected_industry)
            
            # Clear caches before recalculating
            st.session_state.clear_questionnaire_cache = True
            
            logger.info(f"AUTO-FIX: Recalculating with {regulation_for_calc}/{industry_for_calc}")
            st.session_state.results = calculate_compliance_score(
                regulation_for_calc,
                industry_for_calc
            )
            st.success(f"✅ **Auto-fixed questionnaire mismatch!** Now using correct {regulation_for_calc} questionnaire.")
            
            # Reset the flag and rerun
            st.session_state.auto_fixing_mismatch = False
            st.rerun()
        else:
            # If we're still in auto-fix mode, show a simple message
            st.info("🔄 Finalizing questionnaire alignment...")
            st.session_state.auto_fixing_mismatch = False
    
    # Summary section
    st.markdown(f"""
    ### Overall Compliance: {results['overall_score']:.1f}% and <span style='color: {get_compliance_level_color(results['compliance_level'])}; font-weight: bold;'>{results['compliance_level']}</span>
    This report provides a detailed assessment of your organization's compliance with the {format_regulation_name(st.session_state.selected_regulation)}
    across key areas. Review the section scores and recommendations below to identify areas
    for improvement.
    """, unsafe_allow_html=True)
    
    # Create two columns for charts with 1:2 ratio
    col1, col2 = st.columns([1, 2])
    
    # Add gauge chart in the first column
    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=results['overall_score'],
            number={'suffix': '%', 'valueformat': '.0f'},
            domain={'x': [0.1, 0.9], 'y': [0, 0.9]},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 25, 50, 75, 100], 'ticktext': ['0%', '25%', '50%', '75%', '100%']},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 50], 'color': "#ff4b4b"},
                    {'range': [50, 75], 'color': "#ffa64b"},
                    {'range': [75, 100], 'color': "#4bff4b"}
                ]
            },
            title={'text': "Overall Compliance Score"}
        ))
        fig.update_layout(height=300, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Add horizontal bar chart in the second column
    with col2:
        # Get all sections from questionnaire
        questionnaire = st.session_state.current_questionnaire
        all_sections = [section["name"] for section in questionnaire["sections"]]
        
        # Create section scores dataframe with percentage scores and weights, including all sections
        df = pd.DataFrame([
            {
                "Section": section,
                "Score": max(0.1, round(results["section_scores"].get(section, 0) * 100)),
                "Weight": round(next((s['weight'] * 100 for s in questionnaire['sections'] if s['name'] == section), 0), 1)
            }
            for section in all_sections
        ])
        df = df.sort_values(by="Score", ascending=True)
        
        # Create horizontal bar chart with improved color scheme and hover template
        fig = px.bar(
            df, 
            x="Score", 
            y="Section", 
            orientation='h',
            color="Score",
            color_continuous_scale=[[0, "#FF4B4B"], [0.5, "#FF4B4B"], [0.5, "#FFA500"], [0.75, "#FFA500"], [0.75, "#00CC96"], [1, "#00CC96"]],
            range_color=[0, 100],
            labels={"Score": "Compliance Score (%)"}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(automargin=True)
        )
        # Add custom hover template to show weight
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}%<br>Weight: %{customdata:.1f}%<extra></extra>",
            customdata=df["Weight"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Add verification for perfect scores
    all_perfect = True
    all_section_scores = []
    
    for section_name, score in results["section_scores"].items():
        if score is not None:  # Skip sections with no applicable questions
            all_section_scores.append(score)
            if score < 1.0:
                all_perfect = False
                break
    
    if all_perfect and results['overall_score'] < 100:
        st.warning("""
        **Note:** All your section scores show full compliance, but the overall score may be slightly below 100% 
        due to weighting factors or rounding. Your organization has effectively achieved full compliance.
        """)

    # Create dataframe for section scores table
    section_data = []
    none_score_sections = []
    
    for section, score in results["section_scores"].items():
        if score is not None:  # Skip sections with no applicable questions
            status = "High Risk" if score < 0.6 else ("Moderate Risk" if score < 0.75 else "Compliant")
            section_data.append({
                "Section": section,
                "Score (%)": f"{score * 100:.1f}%",
                "Weight": (
                    f"{next((s['weight'] * 100 for s in get_questionnaire(*get_regulation_and_industry_for_loader())['sections'] if s['name'] == section), 0):.1f}%"
                ),
                "Status": status
            })
        else:
            none_score_sections.append(section)
    
    df = pd.DataFrame(section_data)
    
    # Display sections with None scores
    if none_score_sections:
        st.info("The following sections have no score because all questions were marked as 'Not applicable' or had no responses:")
        for section in none_score_sections:
            st.write(f"• {section}")
    
    # Add Recommended Actions section here
    st.subheader("Recommended Actions")

    def clean_recommendation_text(text: str) -> str:
        """Remove all Informatica Solution prefixes and HTML spans from recommendation text."""
        # Remove all HTML spans
        text = re.sub(r"<span[^>]*>Informatica Solution:</span>\s*", "", text, flags=re.IGNORECASE)
        # Remove all plain text occurrences
        text = re.sub(r"Informatica Solution:\s*", "", text, flags=re.IGNORECASE)
        # Remove any leading/trailing whitespace and newlines
        return text.strip()

    if results.get("improvement_priorities"):
        for i, area in enumerate(results["improvement_priorities"][:3]):
            with st.expander(f"Priority {i+1}: {area}"):
                if area in results["recommendations"] and results["recommendations"][area]:
                    for rec in results["recommendations"][area]:
                        st.write(f"• {clean_recommendation_text(rec)}")
                else:
                    st.write("No specific recommendations available for this area.")
    else:
        st.info("No specific priority actions identified based on your assessment results.")
    
    # Add INFA Diagram
    st.subheader("Implementation Framework")
    html_path = os.path.join(config.BASE_DIR, "Assets", "INFA.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        # Use CSS for responsive scaling with container adjustments and new dark background color
        centered_html = f"""
        <style>
        .diagram-section-bg {{
            background: #181c24; /* Dark background color */
            border-radius: 12px;
            padding: 32px 10px 10px 10px;
            margin-bottom: 1rem;
            min-height: 520px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.10);
        }}
        .diagram-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 0;
            margin: 0;
            overflow: auto;
            min-height: 500px;
            background: transparent;
        }}
        .diagram-content {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .diagram-content svg {{
            max-width: 100%;
            height: auto;
            transform-origin: center;
            transition: transform 0.3s ease;
        }}
        @media (max-width: 1200px) {{
            .diagram-section-bg {{ min-height: 470px; }}
            .diagram-content svg {{ transform: scale(0.85); }}
        }}
        @media (max-width: 992px) {{
            .diagram-section-bg {{ min-height: 420px; }}
            .diagram-content svg {{ transform: scale(0.75); }}
        }}
        @media (max-width: 768px) {{
            .diagram-section-bg {{ min-height: 370px; }}
            .diagram-content svg {{ transform: scale(0.65); }}
        }}
        @media (max-width: 576px) {{
            .diagram-section-bg {{ min-height: 320px; }}
            .diagram-content svg {{ transform: scale(0.5); }}
        }}
        </style>
        <div class="diagram-section-bg">
            <div class="diagram-container">
                <div class="diagram-content">
                    {html_content}
                </div>
            </div>
        </div>
        """
        st.components.v1.html(centered_html, height=700, scrolling=True)
    else:
        st.warning("DPDP Implementation Framework diagram not found.")
    
    # Add CLAIRE Diagram with reduced spacing
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    st.subheader("Informatica CLAIRE Framework")
    claire_path = os.path.join(config.BASE_DIR, "Assets", "CLAIRE.html")
    if os.path.exists(claire_path):
        with open(claire_path, "r", encoding="utf-8") as f:
            claire_content = f.read()
        # Use the same dark background and container style as INFA diagram
        centered_html = f"""
        <style>
        .diagram-section-bg {{
            background: #181c24; /* Dark background color */
            border-radius: 12px;
            padding: 32px 10px 10px 10px;
            margin-bottom: 1rem;
            min-height: 520px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.10);
        }}
        .diagram-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 0;
            margin: 0;
            overflow: auto;
            min-height: 500px;
            background: transparent;
        }}
        .diagram-content {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .diagram-content svg {{
            max-width: 100%;
            height: auto;
            transform-origin: center;
            transition: transform 0.3s ease;
        }}
        @media (max-width: 1200px) {{
            .diagram-section-bg {{ min-height: 470px; }}
            .diagram-content svg {{ transform: scale(0.85); }}
        }}
        @media (max-width: 992px) {{
            .diagram-section-bg {{ min-height: 420px; }}
            .diagram-content svg {{ transform: scale(0.75); }}
        }}
        @media (max-width: 768px) {{
            .diagram-section-bg {{ min-height: 370px; }}
            .diagram-content svg {{ transform: scale(0.65); }}
        }}
        @media (max-width: 576px) {{
            .diagram-section-bg {{ min-height: 320px; }}
            .diagram-content svg {{ transform: scale(0.5); }}
        }}
        </style>
        <div class="diagram-section-bg">
            <div class="diagram-container">
                <div class="diagram-content">
                    {claire_content}
                </div>
            </div>
        </div>
        """
        st.components.v1.html(centered_html, height=700, scrolling=True)
    else:
        st.warning("CLAIRE Framework diagram not found.")
    # --- End of commented out section ---

    # Add Not Applicable answers section
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    st.subheader("Answers marked as \"Not Applicable\"")
    
    # Get questionnaire for reference
    regulation_for_loader, industry_for_loader = get_regulation_and_industry_for_loader()
    questionnaire = get_questionnaire(regulation_for_loader, industry_for_loader)
    
    # Find all "Not applicable" responses
    na_responses = []
    for section_idx, section in enumerate(questionnaire["sections"]):
        for q_idx, question in enumerate(section["questions"]):
            response_key = f"s{section_idx}_q{q_idx}"
            response = st.session_state.responses.get(response_key)
            
            if isinstance(response, str) and "not applicable" in response.lower():
                # Get question text
                q_text = question.get("text", question) if isinstance(question, dict) else question
                na_responses.append({
                    "section": section["name"],
                    "question": q_text,
                    "question_number": f"Q{q_idx + 1}"
                })
    
    if na_responses:
        with st.expander("View Not Applicable Responses", expanded=False):
            for item in na_responses:
                # Strip HTML links from question text
                clean_question = re.sub(r'\s*\[<a.*?</a>\]', '', item['question']).strip()
                st.markdown(f"""
                **{item['section']} - {item['question_number']}**  
                {clean_question}
                """)
                st.markdown("---")
    else:
        with st.expander("View Not Applicable Responses", expanded=False):
            st.info("No questions were marked as Not Applicable.")
    
    # Add AI Analysis section header/intro
    st.markdown(get_ai_analysis_css(), unsafe_allow_html=True)
    st.markdown("""
        <div class="ai-analysis-container-header"> <!-- Use a different class if needed -->
            <h3 class="ai-analysis-header">🤖 AI Analysis Summary</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- AI Report Generation and Display ---
    ai_report_content_placeholder = st.empty() # Create a placeholder

    # Initialize cached report key if not exists
    if 'cached_ai_report' not in st.session_state:
        st.session_state.cached_ai_report = None

    # Check if we should regenerate the report
    should_regenerate = (
        st.session_state.cached_ai_report is None or
        st.session_state.get('ai_report_generated') is False
    )

    ai_report = None # Ensure ai_report is defined

    with st.spinner("🔄 Generating detailed AI analysis... (Estimated time: 60–120 seconds)") if should_regenerate else st.container():
        try:
            if should_regenerate:
                generated_report = generate_natural_language_report(st.session_state.results)
                if generated_report and not generated_report.startswith("Error:"):
                    # Clean up the report text
                    cleaned_report = generated_report.strip()
                    cleaned_report = cleaned_report.replace("```markdown", "").replace("```", "")
                    cleaned_report = re.sub(r'</?div[^>]*>', '', cleaned_report, flags=re.IGNORECASE)
                    cleaned_report = cleaned_report.replace("[Insert Date]", st.session_state.get('assessment_date', 'Unknown Date'))
                    cleaned_report = cleaned_report.replace("[Insert Organization Name]", st.session_state.get('organization_name', 'Unknown Organization'))

                    st.session_state.cached_ai_report = cleaned_report
                    st.session_state.ai_report_generated = True
                    ai_report = cleaned_report # Use the newly generated report
                else:
                    st.error("Failed to generate AI analysis. Please try again.")
                    st.session_state.cached_ai_report = None
            else:
                 ai_report = st.session_state.cached_ai_report # Use cached report

            # Display the report content in the placeholder
            if ai_report:
                # Add the previous CSS styling
                st.markdown("""
                    <style>
                    .ai-analysis-container {
                        background: rgba(255, 255, 255, 0.05);
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }
                    .ai-analysis-container h1 {
                        font-size: 1.8em;
                        font-weight: bold;
                        color: white;
                        margin-bottom: 25px;
                        padding-bottom: 15px;
                        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
                    }
                    .ai-analysis-container .report-header {
                        font-size: 1.8em;
                        font-weight: bold;
                        color: white;
                        margin-bottom: 25px;
                        padding-bottom: 15px;
                        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
                    }
                    .ai-analysis-container h2 {
                        color: #6fa8dc;
                        font-size: 1.5em;
                        margin-top: 20px;
                        margin-bottom: 15px;
                    }
                    .ai-analysis-container h3 {
                        color: #6fa8dc;
                        font-size: 1.3em;
                        margin-top: 20px;
                        margin-bottom: 15px;
                    }
                    .ai-analysis-container strong {
                        color: #f8aeae;
                    }
                    .ai-analysis-container ul {
                        margin-left: 20px;
                        margin-bottom: 15px;
                    }
                    .ai-analysis-container li {
                        margin-bottom: 10px;
                        line-height: 1.6;
                    }
                    .ai-analysis-container p {
                        line-height: 1.6;
                        margin-bottom: 15px;
                    }
                    </style>
                """, unsafe_allow_html=True)
                        
                # Process the report to fix the first line
                lines = ai_report.split('\n')
                # Remove any lines before the first Markdown header
                header_idx = next((i for i, l in enumerate(lines) if l.strip().startswith('# ')), 0)
                lines = lines[header_idx:]
                processed_lines = []

                # Robust header extraction using regex
                header_pattern = re.compile(r"^#\s*(.*?)\s*\*\*Overall Compliance Score: ([0-9.]+)%\*\*\s*\*\*Compliance Level: ([^*]+)\*\*")
                header_match = header_pattern.match(lines[0]) if lines else None

                if header_match:
                    title = header_match.group(1).strip()
                    # Round the score to one decimal place
                    try:
                        score = f"{float(header_match.group(2).strip()):.1f}"
                    except Exception:
                        score = header_match.group(2).strip()
                    level = header_match.group(3).strip()
                    color = get_compliance_level_color(level)

                    st.markdown(f"# {title}")
                    st.markdown(f"**Overall Compliance Score: {score}%** **Compliance Level: {level}**")
                    processed_lines = lines[1:]
                else:
                    # Fallback: use session_state values for header if available
                    results = st.session_state.get('results', {})
                    overall_score = results.get('overall_score', 'N/A')
                    compliance_level = results.get('compliance_level', 'N/A')
                    color = get_compliance_level_color(compliance_level) if compliance_level != 'N/A' else '#FF6B6B'
                    fallback_header = f"""<div class=\"report-header\">
                        <div style=\"font-size: 1em; color: white; margin-bottom: 15px;\">Compliance Assessment Report</div>
                        <div style=\"font-size: 1em; line-height: 1.6;\">
                        </div>
                    </div>"""
                    processed_lines.append(fallback_header)
                    processed_lines.extend(lines[1:] if lines else [])

                # Join the processed lines
                processed_report = '\n'.join(processed_lines)
                # Wrap the report in the styled container
                st.markdown(f'<div class="ai-analysis-container">{processed_report}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ai-analysis-container">AI report not available.</div>', unsafe_allow_html=True)


        except Exception as e:
            logger.error(f"Error rendering AI report: {e}")
            st.error("An error occurred while generating the analysis. Please try again.")
            ai_report_content_placeholder.markdown('<div class="ai-analysis-container"><p>Error generating report.</p></div>', unsafe_allow_html=True)
            ai_report = None # Ensure report is None on error


    # --- Download/Regenerate Buttons ---
    if ai_report: # Only show buttons if report exists
        # Add download button styling
        st.markdown(get_download_button_css(), unsafe_allow_html=True)
        
        # Place both buttons in the same row and align them
        button_col1, button_col2 = st.columns([1, 1])
        with button_col1:
            # Store the report content in session state if not already there
            if 'cached_ai_report' not in st.session_state:
                st.session_state.cached_ai_report = ai_report

            # Function to generate PDF when download button is clicked
            def get_pdf_data():
                if 'pdf_data' not in st.session_state:
                    with st.spinner("Generating PDF report..."):
                        try:
                            # Get the original AI report content
                            original_report_content = st.session_state.cached_ai_report
                            if not original_report_content:
                                st.error("No report content available. Please generate a report first.")
                                return None

                            # Get organization name, default if not found
                            org_name = st.session_state.get('organization_name', 'Unknown Organization')
                            current_date = datetime.now().strftime("%B %d, %Y")

                            # Get the logo path and verify it exists
                            logo_path = os.path.join(config.BASE_DIR, "Assets", "@DataINFA.png")
                            logger.info(f"Looking for logo at: {logo_path}")

                            # Add header with logo if available
                            header_content = ""
                            if os.path.exists(logo_path):
                                # Convert logo to base64
                                with open(logo_path, "rb") as f:
                                    logo_base64 = base64.b64encode(f.read()).decode()
                                
                                # Add header with logo and styling
                                header_content = f"""<div style=\"text-align: center; margin-bottom: 30px;\">
                                    <img src=\"data:image/png;base64,{logo_base64}\" style=\"max-width: 32px; height: 32px; margin-bottom: 10px;\">
                                    <h1 style=\"color: #333; margin: 0;\">{org_name}</h1>
                                    <p style=\"color: #666; margin: 5px 0;\">Compliance Assessment Report</p>
                                    <p style=\"color: #666; margin: 5px 0;\">Generated on: {current_date} by DataINFA</p>
                                </div>

                                ---

                                """
                            # Combine header with the report content
                            report_with_header = f"{header_content}{original_report_content}"

                            # Generate PDF
                            pdf_data = convert_markdown_to_pdf(report_with_header, org_name)
                            if pdf_data:
                                st.session_state.pdf_data = pdf_data
                                return pdf_data
                        except Exception as e:
                            logger.error(f"Error generating PDF: {e}")
                            st.error("An error occurred while generating the PDF. Please try again.")
                            return None
                return st.session_state.get('pdf_data')

            # Only show the download button if PDF data is available
            pdf_data = get_pdf_data()
            if pdf_data is not None:
                st.download_button(
                    label="Download Report (PDF)",
                    data=pdf_data,
                    file_name=f"Questionnaire_Assessment_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    help="Download the AI-generated analysis as a PDF document",
                    use_container_width=True,
                    key="download_pdf_button",
                    disabled=not st.session_state.get('cached_ai_report')
                )
            else:
                st.warning("PDF report is not available yet. Please try regenerating the report.")
            # Add a small vertical space between buttons
            st.markdown("<div style='height: 0.5em'></div>", unsafe_allow_html=True)
            # Regenerate button directly below download button
            if st.button("🔄 Regenerate", help="Generate a new AI analysis", use_container_width=True, key="regenerate_button"):
                st.session_state.ai_report_generated = False
                st.rerun()
        # Remove the right_col and any extra alignment divs for these buttons

    def get_image_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Get all image data first
    img1_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-integration-tools-mq.jpg"))
    img2_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "ipaas-mq.jpg"))
    img3_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-governance-mq.jpg"))
    img4_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-quality-mq.png"))
    # Add Gartner Magic Quadrant section with hover effect
    st.markdown("""
        <style>
        .magic-quadrant-section {
            background: #1E1E1E;
            padding: 20px;
                        border-radius: 10px;
            margin: 40px 0;
                    }
        .magic-quadrant-header {
                        color: white;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .magic-quadrant-grid {
            display: flex;
            justify-content: space-between;
            gap: 20px;
                        padding: 10px;
            flex-wrap: nowrap;
        }
        .quadrant-item {
            flex: 1;
            min-width: 200px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .magic-quadrant-title {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 14px;
            font-weight: 500;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .new-badge {
            background: #8A2BE2;
            color: white;
            padding: 2px 8px;
            border-radius: 15px;
            font-size: 10px;
            font-weight: bold;
            margin-left: 6px;
        }
        /* Image container styles */
        .image-container {
            position: relative;
            width: 220px;
            height: 220px;
            transition: transform 0.3s ease;
            cursor: pointer;
        }
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: all 0.3s ease;
            background: white;
            border-radius: 8px;
        }
        .image-container:hover {
            position: relative;
            z-index: 1000;
        }
        .image-container:hover img {
            transform: scale(2.5);
            box-shadow: 0 0 30px rgba(0,0,0,0.7);
        }
        /* Add styles for the link */
        .quadrant-link {
            text-decoration: none;
                        display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render the Magic Quadrant section
    st.markdown(f"""
        <div class="magic-quadrant-section">
            <div class="magic-quadrant-header">
                <span style="color: #FFA500;">Informatica Leadership in Gartner Magic Quadrant</span>
            </div>
            <div class="magic-quadrant-grid">
                <div class="quadrant-item">
                    <div class="magic-quadrant-title">Data Integration Tools</div>
                    <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                        <div class="image-container">
                            <img src="data:image/jpeg;base64,{img1_base64}" alt="Data Integration Tools">
                        </div>
                    </a>
                </div>
                <div class="quadrant-item">
                    <div class="magic-quadrant-title">Integration Platform as a Service (iPaaS)</div>
                    <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                        <div class="image-container">
                            <img src="data:image/jpeg;base64,{img2_base64}" alt="iPaaS">
                        </div>
                    </a>
                </div>
                <div class="quadrant-item">
                    <div class="magic-quadrant-title">Data and Analytics Governance Platforms<span class="new-badge">NEW</span></div>
                    <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                        <div class="image-container">
                            <img src="data:image/jpeg;base64,{img3_base64}" alt="Data Governance">
                        </div>
                    </a>
                </div>
                <div class="quadrant-item">
                    <div class="magic-quadrant-title">Augmented Data Quality Solutions<span class="new-badge">NEW</span></div>
                    <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                        <div class="image-container">
                            <img src="data:image/jpeg;base64,{img4_base64}" alt="Data Quality">
                        </div>
                    </a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


        # Update headers based on regulation
    regulation_for_loader, _ = get_regulation_and_industry_for_loader()
    logger.info(f"[render_assessment] Mapped regulation_for_loader: {regulation_for_loader}")
    
    # Inject penalties section CSS before rendering penalties block
    st.markdown(get_penalties_section_css(), unsafe_allow_html=True)
    if regulation_for_loader == 'DPDP':
        st.markdown("""
            <div class="penalties-container" data-regulation="DPDP">
                <h4 class="penalties-header">Potential Penalties Under DPDP</h4>
                <p class="penalties-text">
                    The Digital Personal Data Protection Act, 2023 prescribes significant penalties for non-compliance:
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'PDPPL':
        st.markdown("""
            <div class="penalties-container" data-regulation="PDPPL">
                <h4 class="penalties-header">Potential Penalties Under Qatar PDPL</h4>
                <p class="penalties-text">
                    Qatar Personal Data Protection Law prescribes the following penalties:
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'NPC':
        st.markdown("""
            <div class="penalties-container" data-regulation="NPC">
                <h4 class="penalties-header">Compliance Requirements Under Qatar NDP</h4>
                <p class="penalties-text">
                    Qatar National Data Policy requires adherence to the following compliance standards:
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'AU_PRIVACY_ACT' or regulation_for_loader == 'OAIC':
        st.markdown("""
            <div class="penalties-container" data-regulation="AU_PRIVACY_ACT">
                <h4 class="penalties-header">Compliance Requirements Under AU_PRIVACY_ACT</h4>
                <p class="penalties-text">
                    AU_PRIVACY_ACT prescribes the following compliance standards:
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'PDPL':
        st.markdown("""
            <div class="penalties-container" data-regulation="PDPL">
                <h4 class="penalties-header">Potential Penalties Under Saudi PDPL</h4>
                <p class="penalties-text">
                    Saudi Personal Data Protection Law prescribes the following penalties:
                </p>
            </div>
        """, unsafe_allow_html=True)
    # Create regulation-specific penalties data
    penalties_data = {}  # Default initialization
    regulation_for_loader, _ = get_regulation_and_industry_for_loader()
    if regulation_for_loader == 'DPDP':
        penalties_data = {
            "Nature of violation/breach": [
                "Failure of data fiduciary to take reasonable security safeguards to prevent personal data breach",
                "Failure to notify Data Protection Board of India and affected data principals in case of personal data breach",
                "Non-fulfilment of additional obligations in relation to personal data of children",
                "Non-fulfilment of additional obligations by significant data fiduciaries",
                "Non-compliance with duties of data principals",
                "Breach of any term of voluntary undertaking accepted by the Data Protection Board",
                "Residuary penalty"
            ],
            "Penalty": [
                "May extend to INR 250 crores",
                "May extend to INR 200 crores",
                "May extend to INR 200 crores",
                "May extend to INR 150 crores",
                "May extend to INR 10,000",
                "Up to the extent applicable",
                "May extend to INR 50 crores"
            ]
        }
    elif regulation_for_loader == 'PDPPL':
        penalties_data = {
            "Violation Type": [
                "General violation of core data protection duties",
                "Serious violations (e.g., breach notification, DPIA, cross-border transfer)",
                "Legal person (organization) violation",
                "Maximum penalty for any infringement"
            ],
            "Penalty Amount (QAR)": [
                "Up to 1,000,000",
                "Up to 5,000,000",
                "Up to 1,000,000",
                "Up to 5,000,000"
            ],
            "Penalty Amount (USD, approx.)": [
                "Up to ~$275,000",
                "Up to ~$1,375,000",
                "Up to ~$275,000",
                "Up to ~$1,375,000"
            ]
        }
    elif regulation_for_loader == 'NPC':
        # NPC focuses on data policy compliance rather than privacy violations
        # You may want to update this section with specific NPC compliance requirements
        penalties_data = {
            "Compliance Area": [
                "Non-compliance with National Data Policy requirements",
                "Failure to establish required data governance structures",
                "Non-adherence to data quality and management standards",
                "Lack of coordination with NPC for data initiatives"
            ],
            "Consequence": [
                "Regulatory review and corrective action requirements",
                "Mandatory implementation of governance frameworks",
                "Required improvement of data management practices",
                "Mandatory coordination and approval processes"
            ]
        }
    elif regulation_for_loader == 'AU_PRIVACY_ACT' or regulation_for_loader == 'OAIC':
        penalties_data = {
            "Nature of violation/breach": [
                "Serious or repeated interference with privacy",
                "Mid-tier civil penalty (interference with privacy)",
                "Administrative breaches (e.g., not having compliant privacy policy, failing to provide opt-outs)",
                "Infringement notices (minor breaches)",
                "Failure to comply with OAIC compliance notice",
                "Criminal penalty for doxxing (malicious public disclosure of personal information)",
                "Statutory tort for serious invasion of privacy"
            ],
            "Penalty": [
                "Greater of AUD 50 million, 3× value of benefit obtained, or 30% of adjusted turnover",
                "AUD 3,300,000 (10,000 penalty units) for corporations; AUD 660,000 (2,000 penalty units) for individuals",
                "AUD 330,000 (1,000 penalty units) for corporations; AUD 66,000 (200 penalty units) for individuals",
                "AUD 19,800–66,000 for corporations; AUD 3,960–66,000 for individuals",
                "AUD 330,000 (1,000 penalty units) for corporations; AUD 66,000 (200 penalty units) for individuals",
                "Up to 6 years' imprisonment (7 years for aggravated cases)",
                "Damages up to AUD 478,550 (non-economic) plus economic loss"
            ]
        }
    elif regulation_for_loader == 'PDPL':
        penalties_data = {
            "Nature of violation/breach": [
                "Disclosure or publication of Sensitive Data with intent to harm or for personal benefit",
                "General violations of PDPL provisions",
                "Failure to implement required security measures",
                "Failure to maintain records of processing activities",
                "Failure to respond to data subject rights requests",
                "Unauthorized cross-border data transfers",
                "Failure to notify data breaches"
            ],
            "Penalty": [
                "Imprisonment up to 2 years or fine up to 3 million SAR, or both",
                "Warning or fine up to 5 million SAR (may be doubled for repeat violations)",
                "Warning or fine up to 5 million SAR",
                "Warning or fine up to 5 million SAR",
                "Warning or fine up to 5 million SAR",
                "Warning or fine up to 5 million SAR",
                "Warning or fine up to 5 million SAR"
            ],
            "Penalty Amount (USD, approx.)": [
                "Up to ~$800,000",
                "Up to ~$1.33 million",
                "Up to ~$1.33 million",
                "Up to ~$1.33 million",
                "Up to ~$1.33 million",
                "Up to ~$1.33 million",
                "Up to ~$1.33 million"
            ]
        }
    
    if penalties_data:
        penalties_df = pd.DataFrame(penalties_data)
        st.markdown(get_penalties_table_css(), unsafe_allow_html=True)
        st.markdown(penalties_df.to_html(classes='penalties-table', escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No penalties data available for the selected regulation.")
    
    # --- Temporarily comment out Countdown section for debugging ---
    # Add the countdown timer with reloader
    st.markdown(get_countdown_section_css(), unsafe_allow_html=True)
    if regulation_for_loader == 'DPDP':
        st.markdown("""
            <div class="countdown-container">
                <h3 class="countdown-header">Time Left to Achieve DPDP Compliance</h3>
                <p class="countdown-text">
                    Your organization must achieve compliance before the tentative deadline: December 31, 2025
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'NPC':
        st.markdown("""
            <div class="countdown-container">
                <h3 class="countdown-header">Qatar National Data Policy Compliance</h3>
                <p class="countdown-text">
                    Ongoing compliance with Qatar's National Data Policy is required for all government and semi-government entities
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'AU_PRIVACY_ACT' or regulation_for_loader == 'OAIC':
        st.markdown("""
            <div class="countdown-container">
                <h3 class="countdown-header">AU_PRIVACY_ACT Compliance</h3>
                <p class="countdown-text">
                    Ongoing compliance with AU_PRIVACY_ACT is required for all government and semi-government entities
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif regulation_for_loader == 'PDPL':
        st.markdown("""
            <div class="countdown-container">
                <h3 class="countdown-header">Saudi PDPL Compliance</h3>
                <p class="countdown-text">
                    Saudi PDPL came into force on September 14, 2023. Organizations must ensure ongoing compliance with all provisions.
                </p>
            </div>
        """, unsafe_allow_html=True)
    # --- End of commented out section ---
    
    # --- End of commented out section ---

    # --- Temporarily comment out final columns/buttons for debugging ---
    col1, col2, col3 = st.columns(3)
    
    with col2:
        # Add Quick AI Data Discovery button
        st.markdown(get_discovery_button_css(), unsafe_allow_html=True)
        
        if st.button("🔍 Ready for a Quick AI Data Discovery ?", use_container_width=True):
            st.session_state.current_page = 'discovery'
            st.rerun()
        
        st.write("")
        st.write("")
        
    with col1: 
        # Download buttons - only show Excel download for admin users
        if st.session_state.get('is_admin', False):
            # Initialize assessment_type if not present
            if 'assessment_type' not in st.session_state:
                st.session_state.assessment_type = 'DPDP'  # Default to DPDP assessment type
            
        # Only show the Admin Excel download link if the user is 'dpdp2025'
        if st.session_state.get('username') == 'dpdp2025':
            excel_link = generate_excel_download_link(
                results,
                st.session_state.organization_name,
                st.session_state.assessment_date,
                st.session_state.assessment_type,
                st.session_state.selected_industry
            )
            st.markdown(excel_link, unsafe_allow_html=True)

def render_recommendations():
    """Render the detailed recommendations page"""
    if not st.session_state.assessment_complete or not st.session_state.results:
        st.warning("Please complete the assessment to view recommendations")
        if st.button("Go to Assessment", type="primary"):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return
    
    results = st.session_state.results
    
    st.header(f"{format_regulation_name(st.session_state.selected_regulation)} Recommendations")
    st.subheader(f"For: {st.session_state.organization_name}")
    
    # Use the consolidated recommendation organization function
    from recommendation_engine import organize_recommendations_by_priority
    recommendations_by_priority = organize_recommendations_by_priority(results)
    
    # Display recommendations by priority
    if recommendations_by_priority['high']:
        st.subheader("High Priority Recommendations", anchor="high-priority")
        st.markdown("These areas require immediate attention to address significant compliance gaps.")
        for item in recommendations_by_priority['high']:
            with st.expander(f"{item['section']} (Score: {item['score']:.1f}%)"):
                for rec in item["recommendations"]:
                    st.write(f"• {rec}")
    
    if recommendations_by_priority['medium']:
        st.subheader("Medium Priority Recommendations", anchor="medium-priority")
        st.markdown("These areas should be addressed after high priority items to improve compliance.")
        for item in recommendations_by_priority['medium']:
            with st.expander(f"{item['section']} (Score: {item['score']:.1f}%)"):
                for rec in item["recommendations"]:
                    st.write(f"• {rec}")
    
    if recommendations_by_priority['low']:
        st.subheader("Low Priority Recommendations", anchor="low-priority")
        st.markdown("These areas are mostly compliant but could benefit from minor improvements.")
        for item in recommendations_by_priority['low']:
            with st.expander(f"{item['section']} (Score: {item['score']:.1f}%)"):
                for rec in item["recommendations"]:
                    st.write(f"• {rec}")
    
    if not (recommendations_by_priority['high'] or recommendations_by_priority['medium'] or recommendations_by_priority['low']):
        st.info("No specific recommendations available based on your assessment responses.")
    
    # Add detailed context for recommendations if available
    regulation_for_loader, industry_for_loader = get_regulation_and_industry_for_loader()
    questionnaire = get_questionnaire(regulation_for_loader, industry_for_loader)
    # Import and use the enhanced recommendations functionality
    from recommendation_engine import get_recommendation_context
    recommendation_context = get_recommendation_context(questionnaire, st.session_state.responses)
    
    if recommendation_context:
        st.subheader("Recommendation Context")
        st.write("Expand each section to see detailed context for the recommendations")
        
        for section, contexts in recommendation_context.items():
            score = results["section_scores"].get(section)
            
            if score is None:
                continue
                
            priority = "high" if score < 0.6 else ("medium" if score < 0.75 else "low")
            priority_emoji = "🔴" if priority == "high" else ("🟠" if priority == "medium" else "🟢")
            
            with st.expander(f"{priority_emoji} {section} - {len(contexts)} recommendations"):
                for context in contexts:  # Fixed missing 'in contexts'
                    st.markdown(f"##### Question {context['question_id']}")
                    st.write(f"**Q:** {context['question_text']}")
                    st.write(f"**Your Response:** {context['response']}")
                    st.markdown(f"**Recommendation:** {context['recommendation']}")
                    st.markdown("---")
    
    # The AI Analysis section previously here has been removed.

def convert_markdown_to_pdf(markdown_content: str, organization_name: str = "Report") -> bytes | None:
    """Convert markdown content to PDF format using the markdown-pdf library."""
    output_file = None
    try:
        # Initialize PDF object with TOC level=2 (headings ##)
        pdf = MarkdownPdf(toc_level=2)

        # Get the logo path and verify it exists
        logo_path = os.path.join(config.BASE_DIR, "Assets", "@DataINFA.png")
        logger.info(f"Looking for logo at: {logo_path}")
        
        # Create a header similar to privacy_policy_analyzer.py (no logo)
        header_content = f"""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #333; margin: 0;">{organization_name}</h1>
    <p style="color: #666; margin: 5px 0;">Compliance Assessment Report</p>
    <p style="color: #666; margin: 5px 0;">Generated on: {datetime.now().strftime('%B %d, %Y')} by DataINFA</p>
</div>

---
"""
        # Combine header with the report content
        full_content = f"{header_content}{markdown_content}"
        
        # Add the entire markdown content as one section
        pdf.add_section(Section(full_content, toc=True))

        # Set PDF metadata
        pdf.meta["title"] = f"{organization_name} - Compliance Assessment Report"
        pdf.meta["author"] = config.APP_TITLE
        pdf.meta["subject"] = "DPDP Compliance Assessment Report"
        pdf.meta["keywords"] = "compliance, DPDP, assessment, analysis"
        pdf.meta["creator"] = "DataInfa Assessment Tool"

        # Create a temporary file path for the PDF output
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
            output_file = temp_pdf_file.name
            logger.info(f"Temporary PDF output path: {output_file}")

        # Save the PDF to the temporary file
        logger.info(f"Attempting conversion and save to: {output_file}")
        pdf.save(output_file)
        logger.info(f"markdown-pdf save operation completed for {output_file}")

        # Check if the output file was created and read it
        if os.path.exists(output_file):
            logger.info(f"Output PDF file exists: {output_file}")
            with open(output_file, 'rb') as f:
                pdf_content = f.read()
            logger.info(f"Successfully read {len(pdf_content)} bytes from {output_file}")
            return pdf_content
        else:
            logger.error(f"Conversion failed. Output PDF file not found: {output_file}")
            st.error("Error: Failed to generate PDF file.")
            return None

    except Exception as e:
            # Catching a general exception as specific errors from markdown-pdf might vary
            logger.error(f"Error during markdown-pdf generation: {e}", exc_info=True)
            st.error(f"An error occurred during PDF generation: {e}")
            return None
    finally:
        # Clean up temporary PDF file
        if output_file and os.path.exists(output_file):
            try:
                os.unlink(output_file)
                logger.info(f"Cleaned up temporary PDF file: {output_file}")
            except Exception as e:
                logger.error(f"Error deleting temporary PDF file {output_file}: {e}")

def render_admin_page():
    """Render the admin page"""
    st.title("Admin Dashboard")
    if not st.session_state.get('is_admin', False):
        st.error("Access denied. Admin privileges required.")
        return
    
    st.subheader("Token Management")
    token_tabs = st.tabs(["Generate Token", "View Tokens", "Revoke Token"])
    
    # Generate Token Tab
    with token_tabs[0]:
        st.write("Create a new access token for an organization")
        
        # Organization name with clear label
        st.markdown("#### Organization Details")
        org_name = st.text_input(
            "Organization Name *", 
            key="new_org_name", 
            placeholder="Enter organization name",
            help="The organization this token will be issued to"
        )
        
        # Add Generated By field
        generated_by = st.text_input(
            "Generated By *", 
            key="generated_by",
            value=st.session_state.get("admin_user", "Admin"),
            placeholder="Enter your name",
            help="Your name or identifier as the token generator"
        )
        
        # Expiry date settings with better alignment
        st.markdown("#### Token Expiration")
        
        # Apply custom CSS for expiry box
        st.markdown(get_expiry_box_css(), unsafe_allow_html=True)
        
        # Force single line with container_width and custom height
        container = st.container()
        with container:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                expiry_days = st.number_input(
                    "Token validity (days)", 
                    min_value=1, 
                    max_value=365, 
                    value=5, 
                    key="expiry_days",
                    help="Number of days this token will remain valid"
                )
            
            with col2:
                expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
                st.markdown(f"""
                <div class="expiry-box">
                    <span style="font-weight: bold;">Expiry date:</span> {expiry_date}
                </div>
                """, unsafe_allow_html=True)
        
        # Generate token button
        if st.button("Generate Token", key="gen_token_btn", type="primary", use_container_width=True):
            if org_name:
                try:
                    # Set token expiry in session state for token_storage to use
                    import token_storage
                    token_storage.TOKEN_EXPIRY_DAYS = expiry_days
                    
                    # Create secure directory if it doesn't exist
                    if not os.path.exists('secure'):
                        os.makedirs('secure', exist_ok=True)
                    
                    # Generate token with the organization name and generated by info
                    new_token = generate_token(org_name, generated_by)
                    if new_token:
                        st.success(f"Token successfully generated for {org_name}!")
                        
                        # Get current timestamp and format it
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                        # Display the token in a more prominent way with updated styling
                        st.markdown(f"""
                        <style>
                        .token-box {{
                            padding: 20px;
                            background: linear-gradient(135deg, #1a2980, #26d0ce);
                            border: 1px solid #4a90e2;
                            border-radius: 8px;
                            margin: 15px 0;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        }}
                        .token-box h3 {{
                            color: white;
                            margin-bottom: 15px;
                            font-size: 1.4rem;
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
                        }}
                        .token-value {{
                            font-family: monospace;
                            font-size: 1.2em;
                            font-weight: bold;
                            padding: 15px;
                            background-color: rgba(255, 255, 255, 0.9);
                            color: #1a2980;
                            border-radius: 5px;
                            word-wrap: break-word;
                            margin-bottom: 15px;
                            border-left: 4px solid #26d0ce;
                        }}
                        .token-details {{
                            margin-top: 15px;
                            font-size: 1em;
                        }}
                        .token-details table {{
                            width: 100%;
                        }}
                        .token-details td {{
                            padding: 6px 0;
                        }}
                        .token-details td:first-child {{
                            font-weight: bold;
                            width: 40%;
                            color: #1a2980;
                        }}
                        </style>
                        <div class="token-box">
                            <h3>🔑 Token Generated</h3>
                            <div class="token-value">{new_token}</div>
                            <div class="token-details">
                                <table>
                                    <tr>
                                        <td>Organization:</td>
                                        <td>{org_name}</td>
                                    </tr>
                                    <tr>
                                        <td>Generated By:</td>
                                        <td>{generated_by}</td>
                                    </tr>
                                    <tr>
                                        <td>Generated on:</td>
                                        <td>{current_time}</td>
                                    </tr>
                                    <tr>
                                        <td>Expires on:</td>
                                        <td>{expiry_date}</td>
                                    </tr>
                                    <tr>
                                        <td>Valid for:</td>
                                        <td>{expiry_days} days</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add copy instructions and security notice below
                        st.info("⚠️ **Copy this token now.** For security reasons, it cannot be retrieved later.")
                        st.warning("**Security Notice:** This token grants access to the assessment platform. Store and transmit it securely.")
                    else:
                        st.error("Failed to generate token. Check logs for details.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter an organization name")

    # View Tokens Tab
    with token_tabs[1]:
        st.write("View existing access tokens")
        if st.button("Refresh Token List", key="refresh_tokens"):
            st.rerun()
        try:
            # Get tokens from secure/tokens.csv
            from token_storage import TOKENS_FILE
            if os.path.exists(TOKENS_FILE):
                # Read the actual CSV structure first to determine the column format
                with open(TOKENS_FILE, 'r') as f:
                    first_line = f.readline().strip()
                    logger.info(f"CSV Header: {first_line}")
                # Read CSV file with correct columns
                tokens_df = pd.read_csv(TOKENS_FILE)
                logger.info(f"CSV columns detected: {list(tokens_df.columns)}")
                
                if not tokens_df.empty:
                    # Rename columns if needed for display consistency
                    column_mapping = {}
                    if 'organization_name' in tokens_df.columns:
                        column_mapping['organization_name'] = 'organization'
                    # Apply column renames if any mappings exist
                    if column_mapping:
                        tokens_df = tokens_df.rename(columns=column_mapping)
                    
                    # Format dates for better readability
                    date_columns = ['created_at', 'expires_at']
                    for col in date_columns:
                        if col in tokens_df.columns:
                            try:
                                # Convert to datetime with flexible parsing
                                tokens_df[col] = pd.to_datetime(tokens_df[col], errors='coerce')
                            except Exception as e:
                                logger.warning(f"Error formatting {col}: {e}")
                    
                    # Add days remaining column
                    if 'expires_at' in tokens_df.columns:
                        current_time = datetime.now()
                        days_remaining = []
                        
                        # Process each row individually
                        for _, row in tokens_df.iterrows():
                            try:
                                if pd.notna(row['expires_at']):
                                    expires = pd.to_datetime(row['expires_at'], errors='coerce')
                                    if pd.notna(expires):
                                        delta = expires - current_time
                                        days = delta.days
                                        days_remaining.append("Expired" if days < 0 else f"{days} days")
                                    else:
                                        days_remaining.append("Unknown")
                                else:
                                    days_remaining.append("Unknown")
                            except Exception as e:
                                logger.warning(f"Error calculating days remaining: {e}")
                                days_remaining.append("Unknown")
                                
                        tokens_df['Days Remaining'] = days_remaining
                    
                    # Define columns to display, make sure they exist in the dataframe
                    preferred_columns = ['organization', 'token', 'generated_by', 'created_at', 'expires_at', 'Days Remaining']
                    display_columns = [col for col in preferred_columns if col in tokens_df.columns]
                    
                    # Final display column renames for better presentation
                    column_renames = {
                        'organization': 'Organization',
                        'token': 'Token',
                        'generated_by': 'Generated By',
                        'created_at': 'Created At',
                        'expires_at': 'Expires At'
                    }
                    # Only select and rename columns that exist
                    tokens_df = tokens_df[display_columns].rename(columns={col: column_renames.get(col, col) for col in display_columns})
                    st.dataframe(tokens_df, use_container_width=True)
                else:
                    st.info("No tokens found")
            else:
                st.info("No tokens have been created yet")
        except Exception as e:
            st.error(f"Error loading tokens: {str(e)}")
            logger.error(f"Token loading error: {str(e)}", exc_info=True)

    # Revoke Token Tab
    with token_tabs[2]:
        st.write("Revoke an existing access token")
        token_to_revoke = st.text_input("Enter token to revoke", key="revoke_token_input")
        if st.button("Revoke Token", key="revoke_btn", type="primary"):
            if token_to_revoke:
                try:
                    # Use imported function
                    if revoke_token(token_to_revoke):
                        st.success(f"Token revoked successfully!")
                    else:
                        st.error("Failed to revoke token. Token may not exist.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a token to revoke")

    # Token Maintenance Section
    st.subheader("Maintenance")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clean up expired tokens", key="cleanup_btn"):
            try:
                count = cleanup_expired_tokens()
                if count > 0:
                    st.success(f"Removed {count} expired tokens")
                else:
                    st.info("No expired tokens found")
            except Exception as e:
                st.error(f"Error during cleanup: {str(e)}")
    with col2:
        if st.button("Export Token Database", key="export_btn"):
            from token_storage import TOKENS_FILE
            if os.path.exists(TOKENS_FILE):
                import base64
                with open(TOKENS_FILE, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="tokens_export.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("No token database found to export")

    

def auto_fill_responses(auto_fill_type):
    """Auto-fill responses based on the selected type"""
    if not st.session_state.get('responses'):
        st.session_state.responses = {}
    
    questionnaire = get_questionnaire(
        st.session_state.selected_regulation,
        st.session_state.selected_industry
    )
    
    for section_idx, section in enumerate(questionnaire["sections"]):
        for q_idx, question in enumerate(section["questions"]):
            response_key = f"s{section_idx}_q{q_idx}"
            
            if auto_fill_type == "All Compliant":
                st.session_state.responses[response_key] = "Yes"
            elif auto_fill_type == "All Non-Compliant":
                st.session_state.responses[response_key] = "No"
            elif auto_fill_type == "All Partially Compliant":
                st.session_state.responses[response_key] = "Partially"
            elif auto_fill_type == "Random Mix":
                import random
                options = ["Yes", "No", "Partially", "Not applicable"]
                st.session_state.responses[response_key] = random.choice(options)

def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        # --- Inject CSS directly for sidebar buttons --- #
        st.markdown("""
            <style>
                /* Center all content in sidebar */
                [data-testid="stSidebarUserContent"] {
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                }

                /* Logo container styling */
                [data-testid="stSidebarUserContent"] div:has(> img) {
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    padding: 0.2rem 0 0.6rem 0 !important;
                    margin: 0 !important;
                    width: 100% !important;
                }

                /* Logo image styling */
                [data-testid="stSidebarUserContent"] img {
                    width: 200px !important;
                    height: auto !important;
                    margin: 0 auto !important;
                    align-items: center !important;
                }

                /* Navigation buttons container */
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] {
                    width: 98% !important;
                    margin: 0.01rem auto !important;
                }

                /* Style the button text itself */
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] > button {
                    width: 100%;
                    padding: 0.5rem 0.75rem;
                    margin: 0.1rem 0;
                    background-color: #23232b !important;
                    color: #fafafa;
                    border: none !important;
                    border-radius: 0.4rem;
                    text-align: left;
                    transition: color 0.2s, background-color 0.2s;
                    box-shadow: none !important;
                }
                
                /* Hover effect - subtle background */
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] > button:hover:not(:disabled) {
                    background-color: rgba(255, 255, 255, 0.05) !important;
                    color: #6fa8dc !important;
                    border: none !important;
                }

                /* Active/Selected state - left border and highlight */
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] > button:focus,
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] > button:active,
                div[data-testid="stSidebarUserContent"] div[data-testid="stButton"] > button[kind="secondary"] {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                    color: #ffffff !important;
                    border-left: 3px solid #6fa8dc !important;
                    padding-left: calc(0.75rem - 3px) !important; /* Adjust padding for border */
                    }
                    </style>
            """, unsafe_allow_html=True)
        # --- End of CSS Injection --- #

        # Logo: Centered using CSS only, no Streamlit columns
        st.markdown(get_logo_css(), unsafe_allow_html=True)
        if os.path.exists(config.LOGO_PATH): 
            st.image(config.LOGO_PATH, width=230)
        else:
            st.warning(f"Logo not found at path: {config.LOGO_PATH}")
        
        # Apply custom CSS for navigation menu
        st.markdown(get_section_navigation_css(), unsafe_allow_html=True)
        
        # Make sure we apply common button CSS
        st.markdown(get_common_button_css(), unsafe_allow_html=True)
        
        # Navigation section title
        
        # Check if assessment parameters are filled AND assessment is started
        assessment_ready = (
            st.session_state.organization_name and 
            st.session_state.organization_name.strip() != "" and 
            st.session_state.selected_regulation and
            st.session_state.selected_industry and
            st.session_state.get('assessment_started', False)  # New condition
        )



        # Define navigation items with conditional display
        nav_items = [
            {"label": "Privacy Policy Analyzer", "key": "nav_home", "page": "welcome", "always_show": True},
            {"label": "Assessment", "key": "nav_assessment", "page": "assessment", "show_if_ready": assessment_ready},
            {"label": "AI Report ✨", "key": "nav_report", "page": "report", "show_if": "assessment_complete"},
            {"label": "AI Data Discovery 🪄", "key": "nav_discovery", "page": "discovery", "show_if": "assessment_complete"},
            {"label": "AI Privacy Policy Analyzer 💫", "key": "nav_privacy", "page": "privacy", "always_show": True},
            {"label": "Admin", "key": "nav_admin", "page": "admin", "show_if": "is_admin"},
            {"label": "FAQ", "key": "nav_faq", "page": "faq", "always_show": True}
        ]
        
        # Fix for button rendering
        for item in nav_items:
            should_show = (
                item.get("always_show", False) or 
                (item.get("show_if") and st.session_state.get(item.get("show_if"), False)) or
                (item.get("show_if_ready") and item.get("show_if_ready"))
            )
            if should_show:
                button_type = "secondary" if st.session_state.current_page == item["page"] else "primary"
                if st.button(
                    item["label"], 
                    key=item["key"], 
                    type=button_type, 
                    use_container_width=True
                ):
                    go_to_page(item["page"])

def render_welcome_page():
    """Render the welcome page"""
    # Center all content
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        # Create container for form elements
        with st.container():
            st.markdown(get_input_label_css(), unsafe_allow_html=True)
            # Add subtitle CSS and subtitle
            st.markdown("""
                <style>
                .subtitle {
                    font-size: 1.5em;
                    color: #FFDB58;
                    font-weight: 500;
                    margin-bottom: 1.2em;
                    margin-top: 0.2em;
                    letter-spacing: 0.01em;
                }
                </style>
            """, unsafe_allow_html=True)
            st.markdown("<div class='subtitle'>Questionnaire-based Policy Assessment</div>", unsafe_allow_html=True)
            
            # 1. Organization Name *
            st.markdown('<p class="input-label">Organization Name *</p>', unsafe_allow_html=True)
            org_name = st.text_input(
                "Organization Name",
                value=st.session_state.organization_name,
                key="org_name_input",
                placeholder="Enter organization name",
                label_visibility="collapsed"
            )
            if org_name != st.session_state.organization_name:
                # Capitalize the organization name
                st.session_state.organization_name = org_name.strip().title()
                # Save organization data
                from data_storage import save_assessment_data
                org_data = {
                    'organization_name': st.session_state.organization_name,
                    'assessment_date': datetime.now().strftime("%Y-%m-%d"),
                    'selected_regulation': st.session_state.selected_regulation,
                    'selected_industry': st.session_state.selected_industry,
                    'responses': {},
                    'assessment_complete': False
                }
                save_assessment_data(org_data)
            
            
            # 2. Country (from PRIVACY_LAWS)
            from privacy_policy_analyzer import PRIVACY_LAWS
            # Define allowed countries directly
            allowed_countries = ["Qatar", "India", "Europe", "Australia", "Saudi Arabia"]
            
            # Initialize session state for country if not exists
            if "selected_country" not in st.session_state:
                st.session_state.selected_country = "Qatar"
            
            # Create the selectbox with the current selection
            selected_country = st.selectbox(
                "Country *",
                options=allowed_countries,
                index=allowed_countries.index(st.session_state.selected_country),
                help="Select the country for compliance assessment"
            )
            
            # Update session state with the selected country
            if selected_country != st.session_state.selected_country:
                st.session_state.selected_country = selected_country
                # Reset industry when country changes
                st.session_state.selected_industry = None

            st.write("")
            
            # 3. Select Industry * (context-sensitive)
            st.markdown('<p class="input-label">Industry *</p>', unsafe_allow_html=True)
            industry_options = []
            if selected_country == "Qatar":
                industry_options = ["Oil and Gas", "General"]
            elif selected_country == "India":
                industry_options = ["Banking and finance", "E-commerce"]
            elif selected_country == "Europe":
                industry_options = ["General", "Banking and finance", "E-commerce"]
            elif selected_country == "Australia":
                industry_options = ["General", "Banking and finance", "E-commerce"]
            elif selected_country == "Saudi Arabia":
                industry_options = ["General", "Banking and finance", "E-commerce"]

            # Initialize industry in session state if not exists or if current industry is invalid
            if "selected_industry" not in st.session_state or st.session_state.selected_industry not in industry_options:
                st.session_state.selected_industry = industry_options[0] if industry_options else None

            # Now render the dropdown 
            selected_industry = st.selectbox(
                "Industry",
                options=industry_options,
                index=industry_options.index(st.session_state.selected_industry) if st.session_state.selected_industry in industry_options else 0,
                label_visibility="collapsed",
                key="industry_select"
            )
            
            # Update session state without forcing rerun
            if selected_industry != st.session_state.selected_industry:
                st.session_state.selected_industry = selected_industry

            st.write("")

            # 4. Regulation (auto-populated, disabled)
            # Determine regulation based on current selections
            if selected_country == "Qatar":
                if selected_industry == "General":
                    regulation_label = "National Data Policy (Qatar)"
                    regulation_key = "NPC"
                else:
                    regulation_label = "Qatar Personal Data Protection Law"
                    regulation_key = "PDPPL"
            elif selected_country == "Europe":
                regulation_label = "General Data Protection Regulation (GDPR)"
                regulation_key = "GDPR"
            elif selected_country == "Australia":
                regulation_label = "Australian Privacy Principles (APPs)"
                regulation_key = "OAIC"
            elif selected_country == "Saudi Arabia":
                regulation_label = "Personal Data Protection Law (PDPL)"
                regulation_key = "PDPL"
            else:  # India
                regulation_label = "Digital Personal Data Protection Act (DPDP)"
                regulation_key = "DPDP"
                
            st.selectbox(
                "Regulation",
                options=[regulation_label],
                index=0,
                disabled=True,
                key=f"regulation_select_{selected_country}_{selected_industry}",
                help="Auto populated based on the selected country and industry"
            )
            st.session_state.selected_regulation = regulation_key
            
            # Centered button with fixed width
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "Start Assessment",
                    type="primary",
                    use_container_width=True,
                ):
                    if not org_name.strip():
                        st.error("Please enter your organization name before starting the assessment.")
                        return
                    # Reset responses and assessment completion status
                    st.session_state.responses = {}
                    st.session_state.assessment_complete = False
                    st.session_state.results = None
                    st.session_state.current_section = 0
                    st.session_state.assessment_started = True
                    logger.info(f"Starting assessment for {org_name}")
                    # Save organization data
                    from data_storage import save_assessment_data
                    org_data = {
                        'organization_name': org_name,
                        'assessment_date': datetime.now().strftime("%Y-%m-%d"),
                        'selected_regulation': st.session_state.selected_regulation,
                        'selected_industry': st.session_state.selected_industry,
                        'responses': {},
                        'assessment_complete': False,
                        'is_start': True  # Add this flag to trigger start notification
                    }
                    save_assessment_data(org_data)
                    go_to_page('assessment')
                    st.rerun()
                # Add a short note below the button, centered
                st.markdown('<div style="margin-top: 0.5em; color: #aaa; font-size: 0.95em; text-align: center;">Estimated completion time: 5–10 minutes.</div>', unsafe_allow_html=True)

def render_dashboard():
    """Render the dashboard view"""
    pass

def render_faq():
    """Render the FAQ view"""
    st.markdown(get_faq_css(), unsafe_allow_html=True)
    st.markdown("<h1 class='faq-header'>Frequently Asked Questions</h1>", unsafe_allow_html=True)
    
    for category, faqs in FAQ_DATA.items():
        st.markdown(f"<h2 class='faq-category'>{category}</h2>", unsafe_allow_html=True)
        for question, answer in faqs.items():
            with st.expander(question):
                st.markdown(answer)

def render_data_discovery():
    """Render the data discovery view"""
    if not st.session_state.assessment_complete:
        st.info("Complete the assessment to access the data discovery tool")
        if st.button("Go to Assessment", type="primary"):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return
    
    # Add custom CSS for data discovery page
    st.markdown(get_data_discovery_css(), unsafe_allow_html=True)

    st.header("AI Data Discovery")
    
    # Import and use the data discovery functionality
    from data_discovery import analyze_ddl_script, render_findings_section, get_recommendations
    
    # File upload for DDL script
    uploaded_file = st.file_uploader("Upload your database DDL script (SQL or TXT format)", type=['sql', 'txt'])
    
    if uploaded_file is not None:
        try:
            ddl_content = uploaded_file.getvalue().decode("utf-8")
            
            with st.spinner("Analyzing database schema..."):
                findings = analyze_ddl_script(ddl_content)
                
                if "error" in findings:
                    st.error(f"Analysis failed: {findings['error']}")
                else:
                    # Display findings
                    render_findings_section(findings)
                    
                    st.subheader("Recommendations")
                    recommendations = get_recommendations(findings)
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
        except Exception as e:
            st.error(f"Error analyzing file: {str(e)}")
    
    # Show example of what will be analyzed
    with st.expander("What will be analyzed?"):
        st.markdown("""
            Our AI will analyze your database schema to identify:

            **Risk Levels:**
            - 🚨 HIGH RISK (Direct Identifiers)
            - ⚠️ MEDIUM RISK (Indirect Identifiers)
            - ℹ️ LOW RISK (Generic Information)

            **Data Categories:**
            - Personal Identifiers (names, emails, IDs)
            - Financial Information (salary, payment details)
            - Health Information (medical records)
            - Biometric Data (fingerprints, facial data)
            - Digital Identifiers (device IDs, IP addresses)
            - Location Data (addresses, coordinates)
            - Professional Data (employment records)

            The analysis will identify specific table and column names containing sensitive data, their risk levels, and data combinations that could reveal personal information.

            Contact info@datainfa.com for further understanding and implementation
        """)
        
    st.markdown(get_penalties_note_css(), unsafe_allow_html=True)
    st.markdown("""
        <div class='penalties-note'>
            ℹ️ We never store your data. We only use it to provide you with a report.
        </div>
    """, unsafe_allow_html=True)

def get_compliance_level_color(level):
    """Return color based on compliance level"""
    colors = {
        "Non-Compliant": "#FF4B4B",  # Red
        "Partially Compliant": "#FFA500",  # Orange
        "Mostly Compliant": "#FFD700",  # Gold
        "Fully Compliant": "#4CAF50"  # Green
    }
    return colors.get(level, "#808080")  # Default to gray if level not found

def convert_for_download():
    """Convert report content to a downloadable PDF format.
    Parameters:
        - None
    Returns:
        - bytes: The binary data of the generated PDF if successful, otherwise None.
    Processing Logic:
        - Retrieves the report content and organization name from session state.
        - Adds a header including current date and optional organization logo.
        - Generates a PDF from combined header and report content, displaying success or error messages accordingly."""
    try:
        # Get the original report content from session state
        original_report_content = st.session_state.get('ai_report_content')
        if not original_report_content:
            st.error("No report content available. Please generate a report first.")
            return None

        # Get organization name
        org_name = st.session_state.get('organization_name', 'Organization')
        current_date = datetime.now().strftime("%B %d, %Y")

        # Add header with logo if available
        logo_path = os.path.join(config.BASE_DIR, "Assets", "DataINFA.png")
        header = f"""#### AI Report generated by DataINFA on: {current_date} for {org_name}

---

"""
        
        # Combine header with the report content
        report_with_header = f"{header}{original_report_content}"
        
        with st.spinner("Generating PDF report..."):
            # Generate PDF
            pdf_data = convert_markdown_to_pdf(report_with_header, org_name)
            if pdf_data:
                st.success("PDF report generated successfully!")
                return pdf_data
            else:
                st.error("Failed to generate PDF report. Please try again.")
                return None
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        st.error("An error occurred while generating the PDF. Please try again.")
        return None

# In the main UI section where the download button is rendered:
if st.session_state.get('ai_report_generated', False):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        # Generate PDF data first
        pdf_data = convert_for_download() if st.session_state.get('ai_report_content') else None
        
        # Only show download button if we have PDF data
        if pdf_data is not None:
            if st.download_button(
                "📥 Download",
                data=pdf_data,
                file_name=f"AI_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                help="Download the report as PDF",
                use_container_width=False
            ):
                pass  # The download will be handled by Streamlit

def render_privacy_policy_analyzer() -> None:
    """Render the redesigned AI Privacy Policy Analyzer page with welcome-page style UI/UX."""
    st.markdown(get_input_label_css(), unsafe_allow_html=True)
    # Add subtitle CSS and subtitle
    st.markdown("""
        <style>
        .subtitle {
            font-size: 1.5em;
            color: #FFDB58;
            font-weight: 500;
            margin-bottom: 1.2em;
            margin-top: 0.2em;
            letter-spacing: 0.01em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    analysis_html = None
    pdf_content = None
    found_url_message = None

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<div class='subtitle'>AI-based Privacy Policy Assessment</div>", unsafe_allow_html=True)
        with st.container():
            # 1. Organization Name *
            st.markdown('<p class="input-label">Organization Name *</p>', unsafe_allow_html=True)
            org_name = st.text_input(
                "Organization Name",
                value=st.session_state.get("ppa_org_name", ""),
                key="ppa_org_name_input",
                placeholder="Enter organization name",
                label_visibility="collapsed"
            )
            if org_name != st.session_state.get("ppa_org_name", ""):
                # Capitalize the organization name
                st.session_state.ppa_org_name = org_name.strip().title()
                # Clear previous analysis when org name changes
                st.session_state.ppa_analysis_html = None
                st.session_state.ppa_pdf_content = None
                st.session_state.ppa_error = None
                st.session_state.ppa_found_url_message = None

            # 2. Country (Qatar/India/Europe/Saudi Arabia only)
            from privacy_policy_analyzer import PRIVACY_LAWS
            country_options = {config["name"]: key for key, config in PRIVACY_LAWS.items()}
            allowed_countries = ["Qatar", "India", "Europe", "Saudi Arabia"]
            country_options = {k: v for k, v in country_options.items() if k in allowed_countries}
            country_names = list(country_options.keys())
            # Set default to 'Qatar' if available, otherwise use the first country
            selected_country = st.session_state.get("ppa_selected_country", "Qatar" if "Qatar" in country_names else country_names[0])
            selected_country = st.selectbox(
                "Country *",
                options=country_names,
                index=country_names.index(selected_country) if selected_country in country_names else 0,
                help="Select the country for privacy policy analysis"
            )
            st.session_state.ppa_selected_country = selected_country
            selected_country_key = country_options[selected_country]

            # 4. Regulation (auto-populated, disabled)
            if selected_country == "Europe":
                regulation_label = "General Data Protection Regulation (GDPR)"
                regulation_key = "GDPR"
            elif selected_country == "Saudi Arabia":
                regulation_label = "Personal Data Protection Law (PDPL)"
                regulation_key = "pdpl_saudi"
            else:
                regulation_label = PRIVACY_LAWS[selected_country_key]["regulation"]
                regulation_key = selected_country_key
            st.selectbox(
                "Regulation",
                options=[regulation_label],
                index=0,
                disabled=True,
                help="Auto populated with the selected country's regulation"
            )
            st.session_state.ppa_selected_regulation = regulation_key
            st.write("")

            # 5. Input Method Dropdown
            st.markdown('<p class="input-label">Input privacy details *</p>', unsafe_allow_html=True)
            input_methods = [
                "Select",  # Add default option
                "Auto-Detect and Analyze Website Policy",
                "Enter Privacy Policy URL",
                "Paste Privacy Policy Text"
            ]
            # Initialize input method in session state if not present
            if "ppa_input_method" not in st.session_state:
                st.session_state.ppa_input_method = "Select"
            
            # Use the session state value for the selectbox
            selected_input_method = st.selectbox(
                "Input Method",
                options=input_methods,
                index=input_methods.index(st.session_state.ppa_input_method),
                key="ppa_input_method",
                label_visibility="collapsed",
                on_change=clear_ppa_analysis_state
            )
            # Clear previous analysis when input method changes
            if selected_input_method != st.session_state.ppa_input_method:
                st.session_state.ppa_analysis_html = None
                st.session_state.ppa_pdf_content = None
                st.session_state.ppa_error = None
                st.session_state.ppa_found_url_message = None
            # Removed direct assignment to st.session_state.ppa_input_method to avoid Streamlit error

            # Input fields for each method
            policy_url: Optional[str] = None
            policy_text: Optional[str] = None
            policy_content: Optional[str] = None
            selected_law_key = selected_country_key

            # Show input for Enter Privacy Policy URL
            if selected_input_method == "Enter Privacy Policy URL":
                st.markdown('<p class="input-label">Privacy Policy URL *</p>', unsafe_allow_html=True)
                policy_url = st.text_input(
                    "Privacy Policy URL",
                    value=st.session_state.get("ppa_policy_url", ""),
                    key="ppa_policy_url_input",
                    placeholder="https://example.com/privacy-policy",
                    label_visibility="collapsed"
                )
                st.session_state.ppa_policy_url = policy_url
            # Show input for Paste Privacy Policy Text
            elif selected_input_method == "Paste Privacy Policy Text":
                st.markdown('<p class="input-label">Paste Privacy Policy Text *</p>', unsafe_allow_html=True)
                policy_text = st.text_area(
                    "Privacy Policy Text",
                    value=st.session_state.get("ppa_policy_text", ""),
                    key="ppa_policy_text_input",
                    placeholder="Paste the full privacy policy text here",
                    label_visibility="collapsed",
                    height=200
                )
                st.session_state.ppa_policy_text = policy_text

            # Reduce ONLY the size of the Start Assessment button (AI Privacy Policy Analyzer)
            st.markdown("""
                <style>
                .compact-center-btn {
                    display: flex;
                    justify-content: center;
                    margin-top: 1em;
                    margin-bottom: 1em;
                }	
                .compact-center-btn button {
                    max-width: 160px !important;
                    min-width: 120px !important;
                    width: 100% !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Initialize button_clicked variable
            button_clicked = False

            # Only show Start Assessment button if a valid input method is selected
            if selected_input_method != "Select":
                st.markdown('<div class="compact-center-btn">', unsafe_allow_html=True)
                button_clicked = st.button(
                    "Start Assessment",
                    type="primary",
                    use_container_width=False,
                    key="ppa_start_assessment_btn"
                )
                st.markdown('</div>', unsafe_allow_html=True)

    # --- OUTSIDE the columns block: render results full-width ---
    # Show error if any
    if st.session_state.get("ppa_error"):
        st.error(st.session_state.ppa_error)
    # Show found url message if any
    if st.session_state.get("ppa_found_url_message"):
        st.markdown(st.session_state.ppa_found_url_message, unsafe_allow_html=True)
    # Show analysis if any
    if st.session_state.get("ppa_analysis_html"):
        st.markdown(get_ai_report_css(), unsafe_allow_html=True)
        # Split the analysis_html into first line (header) and the rest
        analysis_lines = st.session_state.ppa_analysis_html.split('\n', 1)
        if analysis_lines:
            # Inject custom CSS for a smaller header
            st.markdown("""
                <style>
                .policy-analysis-header {
                    font-size: 1.3em;
                    font-weight: 600;
                    color: #6fa8dc;
                    margin-bottom: 0.5em;
                    margin-top: 0.5em;
                }
                </style>
            """, unsafe_allow_html=True)

            # Render the header with the custom class, removing '#' and '**'
            header_text = analysis_lines[0].replace('#', '').replace('**', '').strip()
            st.markdown(f"<div class='policy-analysis-header'>{header_text}</div>", unsafe_allow_html=True)
        rest_of_analysis = analysis_lines[1] if len(analysis_lines) > 1 else ""
        st.markdown(f"""
            <div class="ai-analysis-container">
                {rest_of_analysis}
            </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("ppa_pdf_content"):
            st.markdown(get_download_button_css(), unsafe_allow_html=True)
            st.download_button(
                label=" Download Analysis Report (PDF)",
                data=st.session_state.ppa_pdf_content,
                file_name=f"Privacy_Policy_Assessment_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                help="Download the analysis report as a PDF document",
                use_container_width=True
            )
        
        # --- Insert extra sections here ---
        # 1. Implementation Framework
        st.subheader("Implementation Framework")
        html_path = os.path.join(config.BASE_DIR, "Assets", "INFA.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            centered_html = f"""
            <style>
            .diagram-section-bg {{
                background: #181c24;
                border-radius: 12px;
                padding: 32px 10px 10px 10px;
                margin-bottom: 1rem;
                min-height: 520px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.10);
            }}
            .diagram-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                padding: 0;
                margin: 0;
                overflow: auto;
                min-height: 500px;
                background: transparent;
            }}
            .diagram-content {{
                position: relative;
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .diagram-content svg {{
                max-width: 100%;
                height: auto;
                transform-origin: center;
                transition: transform 0.3s ease;
            }}
            @media (max-width: 1200px) {{
                .diagram-section-bg {{ min-height: 470px; }}
                .diagram-content svg {{ transform: scale(0.85); }}
            }}
            @media (max-width: 992px) {{
                .diagram-section-bg {{ min-height: 420px; }}
                .diagram-content svg {{ transform: scale(0.75); }}
            }}
            @media (max-width: 768px) {{
                .diagram-section-bg {{ min-height: 370px; }}
                .diagram-content svg {{ transform: scale(0.65); }}
            }}
            @media (max-width: 576px) {{
                .diagram-section-bg {{ min-height: 320px; }}
                .diagram-content svg {{ transform: scale(0.5); }}
            }}
            </style>
            <div class="diagram-section-bg">
                <div class="diagram-container">
                    <div class="diagram-content">
                        {html_content}
                    </div>
                </div>
            </div>
            """
            st.components.v1.html(centered_html, height=700, scrolling=True)
        else:
            st.warning("DPDP Implementation Framework diagram not found.")
        # 2. CLAIRE Framework
        st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
        st.subheader("Informatica CLAIRE Framework")
        claire_path = os.path.join(config.BASE_DIR, "Assets", "CLAIRE.html")
        if os.path.exists(claire_path):
            with open(claire_path, "r", encoding="utf-8") as f:
                claire_content = f.read()
            centered_html = f"""
            <style>
            .diagram-section-bg {{
                background: #181c24;
                border-radius: 12px;
                padding: 32px 10px 10px 10px;
                margin-bottom: 1rem;
                min-height: 520px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.10);
            }}
            .diagram-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                padding: 0;
                margin: 0;
                overflow: auto;
                min-height: 500px;
                background: transparent;
            }}
            .diagram-content {{
                position: relative;
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .diagram-content svg {{
                max-width: 100%;
                height: auto;
                transform-origin: center;
                transition: transform 0.3s ease;
            }}
            @media (max-width: 1200px) {{
                .diagram-section-bg {{ min-height: 470px; }}
                .diagram-content svg {{ transform: scale(0.85); }}
            }}
            @media (max-width: 992px) {{
                .diagram-section-bg {{ min-height: 420px; }}
                .diagram-content svg {{ transform: scale(0.75); }}
            }}
            @media (max-width: 768px) {{
                .diagram-section-bg {{ min-height: 370px; }}
                .diagram-content svg {{ transform: scale(0.65); }}
            }}
            @media (max-width: 576px) {{
                .diagram-section-bg {{ min-height: 320px; }}
                .diagram-content svg {{ transform: scale(0.5); }}
            }}
            </style>
            <div class="diagram-section-bg">
                <div class="diagram-container">
                    <div class="diagram-content">
                        {claire_content}
                    </div>
                </div>
            </div>
            """
            st.components.v1.html(centered_html, height=700, scrolling=True)
        else:
            st.warning("CLAIRE Framework diagram not found.")
        # 3. Gartner Magic Quadrant
        def get_image_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        img1_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-integration-tools-mq.jpg"))
        img2_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "ipaas-mq.jpg"))
        img3_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-governance-mq.jpg"))
        img4_base64 = get_image_base64(os.path.join(config.BASE_DIR, "Assets", "data-quality-mq.png"))
        st.markdown("""
            <style>
            .magic-quadrant-section {
                background: #1E1E1E;
                padding: 20px;
                border-radius: 10px;
                margin: 40px 0;
            }
            .magic-quadrant-header {
                color: white;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .magic-quadrant-grid {
                display: flex;
                justify-content: space-between;
                gap: 20px;
                padding: 10px;
                flex-wrap: nowrap;
            }
            .quadrant-item {
                flex: 1;
                min-width: 200px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .magic-quadrant-title {
                color: white;
                text-align: center;
                margin-bottom: 10px;
                font-size: 14px;
                font-weight: 500;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .new-badge {
                background: #8A2BE2;
                color: white;
                padding: 2px 8px;
                border-radius: 15px;
                font-size: 10px;
                font-weight: bold;
                margin-left: 6px;
            }
            .image-container {
                position: relative;
                width: 220px;
                height: 220px;
                transition: transform 0.3s ease;
                cursor: pointer;
            }
            .image-container img {
                width: 100%;
                height: 100%;
                object-fit: contain;
                transition: all 0.3s ease;
                background: white;
                border-radius: 8px;
            }
            .image-container:hover {
                position: relative;
                z-index: 1000;
            }
            .image-container:hover img {
                transform: scale(2.5);
                box-shadow: 0 0 30px rgba(0,0,0,0.7);
            }
            .quadrant-link {
                text-decoration: none;
                display: block;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="magic-quadrant-section">
                <div class="magic-quadrant-header">
                    <span style="color: #FFA500;">Informatica Leadership in Gartner Magic Quadrant</span>
                </div>
                <div class="magic-quadrant-grid">
                    <div class="quadrant-item">
                        <div class="magic-quadrant-title">Data Integration Tools</div>
                        <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                            <div class="image-container">
                                <img src="data:image/jpeg;base64,{img1_base64}" alt="Data Integration Tools">
                            </div>
                        </a>
                    </div>
                    <div class="quadrant-item">
                        <div class="magic-quadrant-title">Integration Platform as a Service (iPaaS)</div>
                        <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                            <div class="image-container">
                                <img src="data:image/jpeg;base64,{img2_base64}" alt="iPaaS">
                            </div>
                        </a>
                    </div>
                    <div class="quadrant-item">
                        <div class="magic-quadrant-title">Data and Analytics Governance Platforms<span class="new-badge">NEW</span></div>
                        <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                            <div class="image-container">
                                <img src="data:image/jpeg;base64,{img3_base64}" alt="Data Governance">
                            </div>
                        </a>
                    </div>
                    <div class="quadrant-item">
                        <div class="magic-quadrant-title">Augmented Data Quality Solutions<span class="new-badge">NEW</span></div>
                        <a href="https://www.informatica.com/lp/gartner-leadership.html" target="_blank" class="quadrant-link">
                            <div class="image-container">
                                <img src="data:image/jpeg;base64,{img4_base64}" alt="Data Quality">
                            </div>
                        </a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # 4. Potential Penalties Under
        st.markdown(get_penalties_section_css(), unsafe_allow_html=True)
        # Use selected regulation for penalties
        regulation_for_loader = st.session_state.get("ppa_selected_regulation", "DPDP")
        st.subheader("Potential Penalties Under " + regulation_label)
        penalties_data = {}
        if regulation_for_loader == 'DPDP':
            penalties_data = {
                "Nature of violation/breach": [
                    "Failure of data fiduciary to take reasonable security safeguards to prevent personal data breach",
                    "Failure to notify Data Protection Board of India and affected data principals in case of personal data breach",
                    "Non-fulfilment of additional obligations in relation to personal data of children",
                    "Non-fulfilment of additional obligations by significant data fiduciaries",
                    "Non-compliance with duties of data principals",
                    "Breach of any term of voluntary undertaking accepted by the Data Protection Board",
                    "Residuary penalty"
                ],
                "Penalty": [
                    "May extend to INR 250 crores",
                    "May extend to INR 200 crores",
                    "May extend to INR 200 crores",
                    "May extend to INR 150 crores",
                    "May extend to INR 10,000",
                    "Up to the extent applicable",
                    "May extend to INR 50 crores"
                ]
            }
        elif regulation_for_loader == 'PDPPL':
            penalties_data = {
                "Violation Type": [
                    "General violation of core data protection duties",
                    "Serious violations (e.g., breach notification, DPIA, cross-border transfer)",
                    "Legal person (organization) violation",
                    "Maximum penalty for any infringement"
                ],
                "Penalty Amount (QAR)": [
                    "Up to 1,000,000",
                    "Up to 5,000,000",
                    "Up to 1,000,000",
                    "Up to 5,000,000"
                ],
                "Penalty Amount (USD, approx.)": [
                    "Up to ~$275,000",
                    "Up to ~$1,375,000",
                    "Up to ~$275,000",
                    "Up to ~$1,375,000"
                ]
            }
        elif regulation_for_loader == 'GDPR':
            penalties_data = {
                "Violation Type": [
                    "General violation of GDPR provisions",
                    "Serious violations (e.g., breach notification, DPIA, cross-border transfer)",
                    "Maximum penalty for any infringement"
                ],
                "Penalty Amount (EUR)": [
                    "Up to 10 million or 2% of global annual turnover",
                    "Up to 20 million or 4% of global annual turnover",
                    "Up to 20 million or 4% of global annual turnover"
                ]
            }
        elif regulation_for_loader == 'pdpl_saudi':
            penalties_data = {
                "Nature of violation/breach": [
                    "Disclosure or publication of Sensitive Data with intent to harm or for personal benefit",
                    "General violations of PDPL provisions",
                    "Failure to implement required security measures",
                    "Failure to maintain records of processing activities",
                    "Failure to respond to data subject rights requests",
                    "Unauthorized cross-border data transfers",
                    "Failure to notify data breaches"
                ],
                "Penalty": [
                    "Imprisonment up to 2 years or fine up to 3 million SAR, or both",
                    "Warning or fine up to 5 million SAR (may be doubled for repeat violations)",
                    "Warning or fine up to 5 million SAR",
                    "Warning or fine up to 5 million SAR",
                    "Warning or fine up to 5 million SAR",
                    "Warning or fine up to 5 million SAR",
                    "Warning or fine up to 5 million SAR"
                ],
                "Penalty Amount (USD, approx.)": [
                    "Up to ~$800,000",
                    "Up to ~$1.33 million",
                    "Up to ~$1.33 million",
                    "Up to ~$1.33 million",
                    "Up to ~$1.33 million",
                    "Up to ~$1.33 million",
                    "Up to ~$1.33 million"
                ]
            }
        else:
            penalties_data = {
                "Violation Type": [
                    "General violation of privacy provisions",
                    "Serious violations",
                    "Maximum penalty for any infringement"
                ],
                "Penalty Amount": [
                    "Up to a significant amount",
                    "Up to a higher amount",
                    "Up to the maximum allowed by law"
                ]
            }
        if penalties_data:
            import pandas as pd
            st.markdown(get_penalties_table_css(), unsafe_allow_html=True)
            penalties_df = pd.DataFrame(penalties_data)
            st.markdown(penalties_df.to_html(classes='penalties-table', escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No penalties data available for the selected regulation.")
        # 5. Quick AI Data Discovery button
        st.markdown(get_discovery_button_css(), unsafe_allow_html=True)
        if st.button("🔍 Ready for a Quick AI Data Discovery ?", use_container_width=True, key="ppa_discovery_btn"):
            st.session_state.current_page = 'discovery'
            st.rerun()
        # --- End extra sections ---
        
        st.markdown("""
            <div style="background: rgba(111, 168, 220, 0.1); padding: 1rem; border-radius: 8px; margin-top: 2rem; border-left: 4px solid #6fa8dc;">
                <strong style="color: #6fa8dc;">Note:</strong> Your privacy policy document is processed securely and is not stored. 
                The analysis is performed in real-time and results are displayed immediately.
            </div>
        """, unsafe_allow_html=True)

    if button_clicked:
        # Validation
        if not org_name.strip():
            st.error("Please enter your organization name before starting the assessment.")
            return
        if selected_input_method == "Enter Privacy Policy URL" and (not policy_url or not policy_url.strip()):
            st.error("Please enter a valid privacy policy URL.")
            return
        if selected_input_method == "Paste Privacy Policy Text" and (not policy_text or not policy_text.strip()):
            st.error("Please paste the privacy policy text.")
            return
        # Clear previous analysis when starting a new assessment
        st.session_state.ppa_analysis_html = None
        st.session_state.ppa_pdf_content = None
        st.session_state.ppa_error = None
        st.session_state.ppa_found_url_message = None
        from privacy_policy_analyzer import find_privacy_policy_url, fetch_policy_content, analyze_privacy_policy
        # Auto-Detect
        if selected_input_method == "Auto-Detect and Analyze Website Policy":
            found_url = find_privacy_policy_url(org_name, country=selected_country)
            if found_url:
                    st.markdown(get_ai_analysis_css(), unsafe_allow_html=True)
                    st.markdown(f"<div class='ai-analysis-container'>Found privacy policy at: <a href='{found_url}' target='_blank'>{found_url}</a></div>", unsafe_allow_html=True)
                    policy_content = fetch_policy_content(found_url)
                    if not policy_content:
                        st.session_state.ppa_error = "Could not extract policy content from the URL."
                        return
            else:
                    st.session_state.ppa_error = "Could not find privacy policy URL."
                    return
        elif selected_input_method == "Enter Privacy Policy URL":
            with st.spinner("Fetching and analyzing privacy policy..."):
                policy_content = fetch_policy_content(policy_url)
                if not policy_content:
                    st.session_state.ppa_error = "Could not fetch or extract content from the provided URL."
                    return
        elif selected_input_method == "Paste Privacy Policy Text":
            policy_content = policy_text
        # Run analysis
        if policy_content:
            with st.spinner(f"Analyzing privacy policy against {regulation_label} requirements... (Estimated time: ~60 seconds)"):
                analysis_result = analyze_privacy_policy(policy_content, selected_law_key, organization_name=org_name)
                if "error" in analysis_result:
                    st.session_state.ppa_error = f"Error analyzing privacy policy: {analysis_result['error']}"
                    return
                analysis_html = analysis_result["analysis"]
                pdf_content = analysis_result.get("pdf_content")
                st.session_state.ppa_error = None
                st.session_state.ppa_analysis_html = analysis_html
                st.session_state.ppa_pdf_content = pdf_content
                # Force a rerun to refresh the page with the new analysis
                st.rerun()

def clear_ppa_analysis_state() -> None:
    """Clear previous Privacy Policy Analyzer analysis state."""
    st.session_state.ppa_analysis_html = None
    st.session_state.ppa_pdf_content = None
    st.session_state.ppa_error = None
    st.session_state.ppa_found_url_message = None
