import os
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
from googlesearch import search
import logging
import openai
import config
from datetime import datetime
import json
import time
import base64
import tempfile
from markdown_pdf import MarkdownPdf, Section

# Define available privacy laws
PRIVACY_LAWS = {
    "dpdp_india": {
        "name": "India",
        "regulation": "Digital Personal Data Protection Act (DPDP)",
        "file_path": "Assets/Documents/DPDP20203.txt",
        "country": "India",
        "website": "https://datainfa.com/dpdp-act/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the Digital Personal Data Protection Act, 2023 (DPDP Act).

Privacy Policy Content:
---------------------
{policy_content}
---------------------

DPDP Act Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the DPDP Act requirements
2. Highlight specific sections of the DPDP Act that are relevant to each finding, make sure to use hyperlink https://datainfa.com/dpdp-act/
3. Provide recommendations for compliance
4. Clearly highlight key issues

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to DPDP Act sections

## Compliance Gaps
- List specific gaps with references to DPDP Act requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant DPDP Act sections
- Compliance status
- Recommendations"""
    },

    "gdpr_europe": {
        "name": "Europe",
        "regulation": "General Data Protection Regulation (GDPR)",
        "file_path": "Assets/Documents/GDPR.txt",
        "country": "Europe",
        "website": "https://gdpr-info.eu/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the General Data Protection Regulation (GDPR).

Privacy Policy Content:
---------------------
{policy_content}
---------------------

GDPR Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the GDPR requirements
2. Highlight specific articles of the GDPR that are relevant to each finding
3. Provide recommendations for compliance
4. Clearly highlight key issues

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to GDPR articles

## Compliance Gaps
- List specific gaps with references to GDPR requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant GDPR articles
- Compliance status
- Recommendations"""
    },

    "pdpl_saudi": {
        "name": "Saudi Arabia",
        "regulation": "Personal Data Protection Law (PDPL)",
        "file_path": "Assets/Documents/PDPL_Saudi.txt",
        "country": "Saudi Arabia",
        "website": "https://datainfa.com/pdpl-saudi/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the Personal Data Protection Law (PDPL) of Saudi Arabia.

Privacy Policy Content:
---------------------
{policy_content}
---------------------

PDPL Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the PDPL requirements
2. Highlight specific sections of the PDPL that are relevant to each finding
3. Provide recommendations for compliance
4. Clearly highlight key issues

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to PDPL sections

## Compliance Gaps
- List specific gaps with references to PDPL requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant PDPL sections
- Compliance status
- Recommendations"""
    },

    "pdpp_oman": {
        "name": "Oman",
        "regulation": "Personal Data Protection Law (PDPP)",
        "file_path": "Assets/Documents/PDPP_Oman.txt",
        "country": "Oman",
        "website": "https://datainfa.com/pdpp-oman/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the Personal Data Protection Law (PDPP) of Oman.

Privacy Policy Content:
---------------------
{policy_content}
---------------------

PDPP Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the PDPP requirements
2. Highlight specific sections of the PDPP that are relevant to each finding
3. Provide recommendations for compliance
4. Clearly highlight key issues

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to PDPP sections

## Compliance Gaps
- List specific gaps with references to PDPP requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant PDPP sections
- Compliance status
- Recommendations"""
    },

    "ndp_qatar": {
        "name": "Qatar",
        "regulation": "Personal Data Privacy Protection Law (PDPPL) by NPC/NPC",
        "file_path": "Assets/Documents/NDP_Qatar.txt",
        "country": "Qatar",
        "website": "https://datainfa.com/pdppl-qatar/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the Personal Data Privacy Protection Law (PDPPL) of Qatar.

Privacy Policy Content:
---------------------
{policy_content}
---------------------

PDPPL Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the PDPPL requirements
2. Highlight specific sections of the PDPPL that are relevant to each finding
3. Provide recommendations for compliance
4. Clearly highlight key issues

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to PDPPL sections

## Compliance Gaps
- List specific gaps with references to PDPPL requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant PDPPL sections
- Compliance status
- Recommendations"""
    },

    "npc_qatar": {
        "name": "Qatar (NPC)",
        "regulation": "National Data Policy (Qatar)",
        "file_path": "Assets/Documents/NDP_Qatar.txt",
        "country": "Qatar",
        "website": "https://www.npc.qa/en/nationaldataprogram/Documents/EnNationalDataPolicy.pdf",
        "prompt_template": """You are a data policy compliance expert. Analyze the following privacy policy against the requirements of the National Data Policy (NDP) of Qatar.

Privacy Policy Content:
---------------------
{policy_content}
---------------------

NDP Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and the NDP requirements
2. Highlight specific sections of the NDP that are relevant to each finding
3. Provide recommendations for compliance with data governance and management standards
4. Clearly highlight key issues related to data strategy, governance, quality, and architecture

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to NDP sections

## Compliance Gaps
- List specific gaps with references to NDP requirements

## Recommendations
- Provide actionable recommendations to address each gap

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant NDP sections
- Compliance status
- Recommendations"""
    },

    "hipaa_usa": {
        "name": "United States",
        "regulation": "Health Insurance Portability and Accountability Act (HIPAA)",
        "file_path": "Assets/Documents/hipaa.txt",
        "country": "United States",
        "website": "https://www.hhs.gov/hipaa/",
        "prompt_template": """You are a privacy policy compliance expert. Analyze the following privacy policy against the requirements of the Health Insurance Portability and Accountability Act (HIPAA).

Privacy Policy Content:
---------------------
{policy_content}
---------------------

HIPAA Requirements:
---------------------
{law_content}
---------------------

Your task is to:
1. Identify any conflicts or gaps between the privacy policy and HIPAA requirements
2. Highlight specific sections of HIPAA that are relevant to each finding
3. Provide recommendations for compliance
4. Clearly highlight key issues, especially regarding Protected Health Information (PHI)

# Privacy Policy Analysis

## Key Findings
- List major findings with specific references to HIPAA sections

## Compliance Gaps
- List specific gaps with references to HIPAA requirements
- Focus on PHI handling and safeguards

## Recommendations
- Provide actionable recommendations to address each gap
- Include specific HIPAA-compliant practices

## Detailed Analysis
For each major section of the privacy policy, provide:
- What was found
- Relevant HIPAA sections
- Compliance status
- Recommendations"""
    }
}

# Configure logging
def setup_privacy_policy_logging():
    """Configure logging for privacy policy analysis."""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs', 'privacy_policy')
    os.makedirs(log_dir, exist_ok=True)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler for all logs with UTF-8 encoding
    log_file = os.path.join(log_dir, f'privacy_analysis_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Error file handler with UTF-8 encoding
    error_file = os.path.join(log_dir, f'privacy_analysis_errors_{datetime.now().strftime("%Y%m%d")}.log')
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Get logger
    logger = logging.getLogger('privacy_policy_analyzer')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers if any
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger

# Initialize logger
logger = setup_privacy_policy_logging()

def find_privacy_policy_url(organization_name: str, country: str = None, num_results: int = 5) -> Optional[str]:
    """Find privacy policy URL using Google search with country context."""
    logger.info(f"Searching privacy policy for organization: {organization_name} in country: {country}")
    query = f"{organization_name} privacy policy {country if country else ''}".strip()
    try:
        search_results = list(search(query, num_results=num_results, lang="en"))
        if not search_results:
            logger.warning(f"No search results found for {organization_name}")
            return None

        for url in search_results:
            if 'privacy' in url.lower() or 'policy' in url.lower() or 'legal' in url.lower():
                logger.info(f"Found privacy policy URL for {organization_name}: {url}")
                return url
        
        logger.info(f"Using first search result for {organization_name}: {search_results[0]}")
        return search_results[0]
    except Exception as e:
        logger.error(f"Error finding privacy policy URL for {organization_name}: {e}")
        return None

def fetch_policy_content(url: str, max_retries: int = 3, retry_delay: int = 2, verify_ssl: bool = True) -> Optional[str]:
    """Fetch and extract privacy policy content from URL."""
    logger.info(f"Fetching privacy policy content from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    for attempt in range(max_retries):
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                logger.info(f"Added https:// prefix to URL: {url}")

            session = requests.Session()
            
            # First try with SSL verification
            try:
                response = session.get(url, headers=headers, timeout=30, verify=verify_ssl)
                response.raise_for_status()
            except requests.exceptions.SSLError as ssl_error:
                logger.warning(f"SSL verification failed on attempt {attempt + 1}, trying without verification")
                # If SSL verification fails, try without verification
                response = session.get(url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
            
            logger.debug(f"Successfully fetched content from {url} on attempt {attempt + 1}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            removed_elements = 0
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript']):
                element.decompose()
                removed_elements += 1
            logger.debug(f"Removed {removed_elements} unwanted elements")
            
            # Try to find main content
            content = None
            selectors = [
                'main', 'article',
                {'role': 'main'},
                {'class_': re.compile(r'(content|main|policy|privacy)', re.I)},
                {'id': re.compile(r'(content|main|policy|privacy)', re.I)}
            ]
            
            for selector in selectors:
                if isinstance(selector, str):
                    content = soup.find(selector)
                else:
                    content = soup.find(attrs=selector)
                if content:
                    logger.debug(f"Found content using selector: {selector}")
                    break
            
            if not content:
                logger.warning("No specific content container found, using body or full document")
                content = soup.body if soup.body else soup
                
            # Clean up the text
            text = content.get_text(separator='\n', strip=True)
            
            # Post-processing
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(line for line in lines if line)
            
            if not text:
                logger.error("No content extracted from URL")
                return None
                
            logger.info(f"Successfully extracted {len(text)} characters of content")
            return text

        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"SSL verification failed after {max_retries} attempts")
                return None
            time.sleep(retry_delay)

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Connection failed after {max_retries} attempts")
                return None
            time.sleep(retry_delay)

        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Request timed out after {max_retries} attempts")
                return None
            time.sleep(retry_delay)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None

        except Exception as e:
            logger.error(f"Error processing content from URL {url}: {e}")
            return None

    return None

def get_law_content(law_key: str) -> Optional[str]:
    """Get the content of the specified privacy law."""
    try:
        law_config = PRIVACY_LAWS.get(law_key)
        if not law_config:
            logger.error(f"Law key {law_key} not found in PRIVACY_LAWS")
            return None
            
        file_path = os.path.join(os.path.dirname(__file__), law_config["file_path"])
        if not os.path.exists(file_path):
            logger.error(f"Law file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
        
    except Exception as e:
        logger.error(f"Error reading law content: {e}")
        return None

def analyze_privacy_policy(policy_content: str, law_key: str, organization_name: str = "Organization") -> Dict:
    """
    Analyze a privacy policy against the specified law requirements.
    
    Args:
        policy_content (str): The content of the privacy policy to analyze
        law_key (str): The key of the law to analyze against (e.g., 'dpdp_india')
        organization_name (str): Name of the organization for the PDF report
        
    Returns:
        Dict: Analysis results including compliance status, recommendations, and PDF content
    """
    try:
        # Check if policy_content is empty or None
        if not policy_content or policy_content.strip() == "":
            logger.error("Empty policy content provided")
            return {"error": "Empty policy content provided"}
        
        # Get the law content
        law_content = get_law_content(law_key)
        if not law_content:
            logger.error(f"No content found for law: {law_key}")
            return {"error": f"Could not find content for {law_key}"}
        
        # Get the law configuration
        law_config = PRIVACY_LAWS[law_key]
        
        # Get the analysis prompt template for this law
        prompt_template = law_config["prompt_template"]
        
        # Create the analysis prompt
        analysis_prompt = prompt_template.format(
            policy_content=policy_content,
            law_content=law_content,
            law_name=law_config["name"],
            law_country=law_config["country"]
        )
        
        # Make the API call to OpenRouter
        api_key = config.get_ai_api_key()
        if not api_key:
            logger.error("API key not found in configuration")
            return {"error": "API key not found"}
            
        # Log the request details
        logger.info(f"Sending request to OpenRouter for {law_config['name']} analysis")

        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://datainfa.com",
                "X-Title": "Compliance Assessment Tool",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {"role": "system", "content": f"You are a {law_config['name']} compliance expert analyzing privacy policies."},
                    {"role": "user", "content": analysis_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 15000
            }
        )
        
        # Log the response status
        logger.info(f"Received response from OpenRouter with status code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code}")
            logger.error(f"API response: {response.text}")
            return {"error": f"API error: {response.status_code}"}
            
        result = response.json()
        analysis = result["choices"][0]["message"]["content"].strip()
        logger.info("Successfully received analysis from OpenRouter")
        
        # Clean the analysis to remove any follow-up questions or prompts
        analysis = clean_analysis_content(analysis)
        
        # Generate PDF report
        pdf_content = generate_privacy_policy_pdf(
            {"analysis": analysis},
            organization_name=organization_name,
            law_key=law_key
        )
        
        return {
            "analysis": analysis,
            "law_name": law_config["name"],
            "law_country": law_config["country"],
            "pdf_content": pdf_content
        }
        
    except Exception as e:
        logger.error(f"Error analyzing privacy policy: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

def generate_privacy_policy_pdf(analysis_result: Dict, organization_name: str = "Organization", law_key: str = "dpdp_india") -> Optional[bytes]:
    """
    Generate a PDF report from the privacy policy analysis results.
    
    Args:
        analysis_result: Dictionary containing the analysis results
        organization_name: Name of the organization
        law_key: Key of the privacy law used for analysis
        
    Returns:
        bytes: PDF file content as bytes, or None if generation fails
    """
    output_file = None
    try:
        # Initialize PDF object with TOC level 2 (headings ##)
        pdf = MarkdownPdf(toc_level=2)
        
        # Get law information first
        law_info = PRIVACY_LAWS.get(law_key, {})
        law_name = law_info.get("name", "Privacy Law")
        law_country = law_info.get("country", "")
        
        # Always use a text-only header (no logo)
        header_content = f"""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #333; margin: 0;">{organization_name}</h1>
    <p style="color: #666; margin: 5px 0;">Privacy Policy Analysis Report</p>
    <p style="color: #666; margin: 5px 0;">Analyzed against: {law_name}</p>
    <p style="color: #666; margin: 5px 0;">Generated on: {datetime.now().strftime('%B %d, %Y')} by DataINFA</p>
</div>

---
"""
        
        # Get the analysis content
        analysis_content = analysis_result.get("analysis", "No analysis available.")
        
        # Combine header with the analysis content
        full_content = header_content + analysis_content
        
        # Add the content as a section
        pdf.add_section(Section(full_content, toc=True))
        
        # Set PDF metadata
        pdf.meta["title"] = f"{organization_name} - Privacy Policy Analysis"
        pdf.meta["author"] = config.APP_TITLE
        pdf.meta["creator"] = "DataInfa Privacy Policy Analyzer"
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
            output_file = temp_pdf_file.name
            logger.info(f"Temporary PDF output path: {output_file}")
        
        # Save the PDF
        logger.info(f"Attempting to save PDF to: {output_file}")
        pdf.save(output_file)
        logger.info(f"PDF save operation completed for {output_file}")
        
        # Read and return the PDF content
        if os.path.exists(output_file):
            logger.info(f"Reading PDF content from: {output_file}")
            with open(output_file, 'rb') as f:
                pdf_content = f.read()
            logger.info(f"Successfully read {len(pdf_content)} bytes from PDF")
            return pdf_content
        else:
            logger.error(f"PDF file not found at: {output_file}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return None
        
    finally:
        # Clean up temporary file
        if output_file and os.path.exists(output_file):
            try:
                os.unlink(output_file)
                logger.info(f"Cleaned up temporary PDF file: {output_file}")
            except Exception as e:
                logger.error(f"Error deleting temporary PDF file {output_file}: {e}")