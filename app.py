"""
Multi-Regulation Compliance Assessment Tool

This application helps organizations assess their compliance with various 
data protection regulations across different industries.

Main entry point that initializes the application and handles page routing.
"""

import streamlit as st

# Set sidebar state based on session flag and current page
if st.session_state.get('current_page') == 'report' and st.session_state.get('collapse_sidebar', False):
    st.set_page_config(
        page_title="Data Protection Compliance Assessment",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.session_state.collapse_sidebar = False  # Reset after collapsing
else:
    st.set_page_config(
        page_title="Data Protection Compliance Assessment",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import config  # Import config after st.set_page_config

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Reduce logging frequency for timer updates
logging.getLogger('__main__').setLevel(logging.INFO)
logging.getLogger('assessment').setLevel(logging.INFO)
logging.getLogger('root').setLevel(logging.INFO)  # Changed from WARNING to INFO

# Setup logging configuration before any other imports
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Changed from WARNING to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)  # Add StreamHandler for terminal output
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Add test log message to verify logging is working
logger.info("Application started - Logging initialized")

# Load environment variables silently
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Check for API key without logging
api_key = os.environ.get("COMPLIANCE_AI_API_KEY")

# Continue with the rest of the imports
from helpers import initialize_session_state
from assessment import get_questionnaire
from views import (
    render_landing_page,
    render_header, 
    render_sidebar, 
    render_welcome_page, 
    render_assessment, 
    render_report, 
    render_data_discovery,
    render_privacy_policy_analyzer,
    render_admin_page,
    render_faq
)

# Initialize session state
initialize_session_state()

# Ensure assessment_type is initialized in session state
if 'assessment_type' not in st.session_state:
    st.session_state.assessment_type = 'PDPPL'

# Check authentication
if not st.session_state.get('authenticated', False):
    render_landing_page()
else:
    # Main application flow
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
    if 'assessment_date' not in st.session_state:
        st.session_state.assessment_date = datetime.now().strftime("%Y-%m-%d")
    if 'selected_regulation' not in st.session_state:
        st.session_state.selected_regulation = "DPDP"
    if 'selected_industry' not in st.session_state:
        st.session_state.selected_industry = "general"

    # Main app logic
    def main():
        """Main application function that renders the appropriate page"""
        try:
            # Render header
            render_header()
            
            # Render sidebar
            render_sidebar()
            
            # Render current page
            if st.session_state.current_page == 'welcome':
                render_welcome_page()
            elif st.session_state.current_page == 'assessment':
                render_assessment()
            elif st.session_state.current_page == 'report' and st.session_state.get('assessment_complete', False):
                render_report()
            elif st.session_state.current_page == 'discovery' and st.session_state.get('assessment_complete', False):
                render_data_discovery()
            elif st.session_state.current_page == 'privacy':
                render_privacy_policy_analyzer()
            elif st.session_state.current_page == 'faq':
                render_faq()
            elif st.session_state.current_page == 'admin' and st.session_state.get('is_admin', False):
                render_admin_page()
            else:
                render_welcome_page()
                
        except Exception as e:
            logger.error(f"Error in main application: {str(e)}", exc_info=True)
            st.error("An unexpected error occurred. Please try refreshing the page.")

    if __name__ == "__main__":
        main()