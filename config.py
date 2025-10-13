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
# Default to Azure unless overridden (keeps ability to switch providers if needed)
AI_PROVIDER = os.getenv("AI_PROVIDER", "azure").lower()

# --- Read API keys: Prioritize Streamlit Secrets, fallback to environment variables --- #

def get_secret_or_env(secret_name: str, env_var_name: str) -> Optional[str]:
    """Return a secret value from Streamlit secrets or environment variables.

    This function first checks Streamlit's secrets for several possible key names
    to accommodate different naming conventions used in ``secrets.toml``.
    It will try, in order: ``secret_name``, ``env_var_name``, ``secret_name.upper()``,
    and ``env_var_name.lower()``. If none are present, it falls back to
    ``os.getenv(env_var_name)``.

    Args:
        secret_name: Preferred key to look up in ``st.secrets`` (usually lowercase).
        env_var_name: Environment variable name to fall back to (usually uppercase).

    Returns:
        The resolved secret value if found; otherwise ``None``.
    """
    key: Optional[str] = None
    try:
        # Read from Streamlit Secrets when available (works on Streamlit Cloud too)
        if hasattr(st, 'secrets'):
            candidate_keys = [
                secret_name,
                env_var_name,
                secret_name.upper(),
                env_var_name.lower(),
            ]
            for candidate in candidate_keys:
                try:
                    if candidate in st.secrets:
                        key_raw = st.secrets.get(candidate)
                        if key_raw is not None:
                            if not isinstance(key_raw, str):
                                key_raw = str(key_raw)
                            key = key_raw.strip().strip('"').strip("'")
                            logger.debug(f"Loaded {candidate} from Streamlit Secrets.")
                            return key
                except Exception:
                    # Some environments may raise during early access; try next
                    continue
    except Exception as e:
        logger.debug(f"Could not access st.secrets for {secret_name}/{env_var_name}: {e}")

    # Fallback to environment variable if not found in secrets or secrets inaccessible
    key_raw = os.getenv(env_var_name)
    if key_raw:
        # Clean the key: remove whitespace and surrounding quotes
        key = key_raw.strip().strip('"').strip("'")
        logger.debug(f"Loaded {env_var_name} from environment variables.")
        return key

    logger.warning(
        f"API Key not found in Streamlit Secrets ('{secret_name}'/'{env_var_name}') or environment ('{env_var_name}')."
    )
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

# ----------------- Azure OpenAI configuration -----------------
try:
    # Import optionally to avoid hard dependency at import time if not used
    from openai import AzureOpenAI  # type: ignore
except Exception:
    AzureOpenAI = None  # type: ignore

# Read Azure OpenAI settings from secrets/env
AZURE_OPENAI_ENDPOINT: Optional[str] = get_secret_or_env("azure_openai_endpoint", "AZURE_OPENAI_ENDPOINT") or ""
AZURE_OPENAI_API_KEY: Optional[str] = get_secret_or_env("azure_openai_api_key", "AZURE_OPENAI_API_KEY") or ""
AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")

_azure_client_instance = None

def get_azure_client() -> Optional["AzureOpenAI"]:
    """Return a cached Azure OpenAI client if configured.

    Returns:
        Optional[AzureOpenAI]: Initialized client or None if misconfigured.
    """
    global _azure_client_instance
    if _azure_client_instance is not None:
        return _azure_client_instance
    if AzureOpenAI is None:
        logger.error("openai package missing or outdated; cannot import AzureOpenAI")
        return None
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        logger.error("Azure OpenAI configuration missing; set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        return None
    try:
        logger.info(
            "Initializing Azure OpenAI client (endpoint=%s, version=%s)",
            AZURE_OPENAI_ENDPOINT,
            AZURE_OPENAI_API_VERSION,
        )
        _azure_client_instance = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
        )
        return _azure_client_instance
    except Exception as exc:
        logger.error("Failed to initialize Azure OpenAI client: %s", exc)
        return None

def get_azure_deployment() -> str:
    """Return the Azure OpenAI deployment name to use for chat completions."""
    return AZURE_OPENAI_DEPLOYMENT
