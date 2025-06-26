"""
Configuration settings for the Compliance Assessment Tool.

This module contains constants and settings used throughout the application.
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
import streamlit as st # Import streamlit

# Load environment variables from .env file (for local dev fallback)
load_dotenv()

logger = logging.getLogger(__name__)

# Get absolute path of the application root
if getattr(sys, 'frozen', False):
    # Running as bundled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running from source
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger.info(f"Base directory: {BASE_DIR}")
# Use absolute paths for questionnaires directory
QUESTIONNAIRE_DIR = os.path.join(BASE_DIR, "Questionnaire")
DATA_DIR = os.path.join(BASE_DIR, "data")
# Define logo path relative to project root for st.image
LOGO_PATH = os.path.join(BASE_DIR, "Assets", "DataINFA.png")

# Ensure critical directories exist
for directory in [QUESTIONNAIRE_DIR, os.path.join(BASE_DIR, "data"), os.path.join(BASE_DIR, "secure")]:
    os.makedirs(directory, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

# App settings
APP_TITLE = "Compliance Assessment Tool"
APP_ICON = "🔐"
APP_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Available regulations and industries
REGULATIONS = {
    "DPDP": "Digital Personal Data Protection Act (India)",
    "PDPPL": "Personal Data Privacy Protection Law (Qatar)",
    "NPC": "National Data Policy (Qatar)",
    "ndp_qatar": "Personal Data Privacy Protection Law (Qatar)"  # Add mapping for ndp_qatar
}

# Industry-to-filename mapping
# This maps industry codes to their corresponding JSON filenames (without the .json extension)
# Case-insensitive industry mapping
INDUSTRY_FILENAME_MAP = {
    "DPDP": {
        "general": "Banking and finance",
        "banking": "Banking and finance",
        "banking and finance": "Banking and finance",
        "e-commerce": "E-commerce",
        "ecommerce": "E-commerce",
        "new": "Banking and finance",
        "new banking fin": "Banking and finance"
    },
    "NPC": {
        "general": "npc"
    }
}

# Display names for industries
INDUSTRY_DISPLAY_NAMES = {
    "Banking and finance": "Financial Services",
    "E-commerce": "E-commerce & Retail",
    "npc": "General",
    # "general": "General Industry"
}

def get_available_regulations() -> Dict[str, str]:
    """Get available regulations"""
    return REGULATIONS

def get_available_industries(regulation_code: str) -> Dict[str, str]:
    """Get available industries for a regulation"""
    try:
        regulation_dir = os.path.join(QUESTIONNAIRE_DIR, regulation_code)
        industries = {}
        
        # Add default industry options from mapping
        if regulation_code in INDUSTRY_FILENAME_MAP:
            industries.update({k.lower(): v for k, v in INDUSTRY_FILENAME_MAP[regulation_code].items()})
        
        # Add industries from files if directory exists
        if os.path.isdir(regulation_dir):
            files = [f for f in os.listdir(regulation_dir) if f.endswith('.json')]
            for file in files:
                industry_code = os.path.splitext(file)[0].lower()
                base_name = os.path.splitext(file)[0]
                industry_name = INDUSTRY_DISPLAY_NAMES.get(base_name, base_name.replace('_', ' ').title())
                industries[industry_code] = industry_name
        else:
            logging.warning(f"Regulation directory not found: {regulation_dir}")
        
        # Always return at least one industry option
        if not industries:
            industries = {"general": "General Industry"}
            
        return industries
    except Exception as e:
        logging.error(f"Error getting available industries: {str(e)}")
        return {"general": "General Industry"}



# AI Report Generation settings
AI_ENABLED = True
AI_PROVIDER = "openrouter"

# --- Read API keys: Prioritize Streamlit Secrets, fallback to environment variables --- #

def get_secret_or_env(secret_name: str, env_var_name: str) -> Optional[str]:
    """
    Retrieve a secret value from Streamlit secrets or environment variables.
    
    Attempts to obtain the specified secret first from Streamlit's `st.secrets`, and if not found, from the corresponding environment variable. Cleans the retrieved value by stripping whitespace and surrounding quotes.
    
    Parameters:
        secret_name (str): The key name to look up in Streamlit secrets.
        env_var_name (str): The environment variable name to use as a fallback.
    
    Returns:
        Optional[str]: The cleaned secret value if found, otherwise None.
    """
    key = None
    try:
        # Check if running in Streamlit context and secrets exist
        if hasattr(st, 'secrets') and secret_name in st.secrets:
             key_raw = st.secrets.get(secret_name)
             if key_raw:
                 # Clean the key: remove whitespace and surrounding quotes
                 key = key_raw.strip().strip('"').strip("'")
                 logger.debug(f"Loaded {secret_name} from Streamlit Secrets.")
                 return key
    except Exception as e:
        # st.secrets might not be available during certain phases or tests
        logger.debug(f"Could not access st.secrets for {secret_name}: {e}")

    # Fallback to environment variable if not found in secrets or secrets inaccessible
    key_raw = os.getenv(env_var_name)
    if key_raw:
         # Clean the key: remove whitespace and surrounding quotes
         key = key_raw.strip().strip('"').strip("'")
         logger.debug(f"Loaded {env_var_name} from environment variables.")
         return key

    logger.warning(f"API Key not found in Streamlit Secrets ('{secret_name}') or environment ('{env_var_name}').")
    return None

api_key_1 = get_secret_or_env("openrouter_api_key_1", "OPENROUTER_API_KEY_1")
api_key_2 = get_secret_or_env("openrouter_api_key_2", "OPENROUTER_API_KEY_2")
api_key_3 = get_secret_or_env("openrouter_api_key_3", "OPENROUTER_API_KEY_3")
# --- End API Key Reading --- #

# Filter out any keys that were not found (returned None)
API_KEYS = [key for key in [api_key_1, api_key_2, api_key_3] if key]
if not API_KEYS:
    logger.error("CRITICAL: No OpenRouter API keys found in Streamlit Secrets or environment variables. AI features will likely fail.")
else:
    logger.info(f"Loaded {len(API_KEYS)} API key(s).")

# API key rotation settings
_current_api_key_index = 0

def get_ai_api_key():
    """Get the API key for AI services with rotation support"""
    global _current_api_key_index
    if not API_KEYS:
        logger.warning("No API keys loaded from environment variables.")
        return None # Return None if no keys are available
        
    # Ensure index is valid
    if _current_api_key_index >= len(API_KEYS):
        _current_api_key_index = 0 # Reset index if out of bounds
        
    key = API_KEYS[_current_api_key_index]
    # Remove "Bearer " prefix if present
    return key.replace("Bearer ", "") if key and key.startswith("Bearer ") else key

def rotate_api_key():
    """Rotate to the next available API key"""
    global _current_api_key_index
    if not API_KEYS or len(API_KEYS) <= 1:
        logger.debug("API key rotation skipped: Only one or zero keys available.")
        return get_ai_api_key() # Return current key if rotation is not possible
        
    _current_api_key_index = (_current_api_key_index + 1) % len(API_KEYS)
    logger.info(f"Rotating to API key index {_current_api_key_index}")
    return get_ai_api_key()

# Update the getter function to handle missing keys better
def get_ai_enabled():
    """Get whether AI report generation is enabled"""
    return AI_ENABLED

def get_ai_provider():
    """Get the AI provider to use"""
    return AI_PROVIDER
