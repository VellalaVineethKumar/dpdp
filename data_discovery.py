import pandas as pd
import streamlit as st
import sqlparse
import re
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime
import openai
import config
import logging
import requests

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

SENSITIVE_DATA_PROMPT = """
# DPDP Data Discovery Analysis
Analyze this database schema for potential DPDP (Digital Personal Data Protection) sensitive data fields.
Present your findings in a clear, visually organized format.

## Categories for Analysis

### Personal Identifiers
- Names and contact details (name, address, phone, email)
- Government IDs (Aadhaar, PAN, passport, licenses)
- Family information (relationships, dependents)

### Financial Information
- Banking details (account numbers, IFSC codes)
- Payment information (card numbers, UPI IDs)
- Financial history (income, transactions)

### Health Information
- Medical records and history
- Treatment information
- Insurance details

### Biometric Data
- Fingerprints and facial data
- Voice patterns
- Genetic information

### Digital Identifiers
- Device IDs and IP addresses
- Browser data and cookies
- Online tracking information

### Location Data
- GPS coordinates
- Movement patterns
- Geographical tracking

### Professional Data
- Employment history
- Performance records
- Professional certifications

## Schema for Analysis:
{schema}

## Required Output Format

###  Personal data fields Analysis
For each category, organize fields by risk level:
🚨 **HIGH RISK** - Direct identifiers, unique personal data
⚠️ **MEDIUM RISK** - Indirect identifiers, combinable data
ℹ️ **LOW RISK** - Generic or public information

### Protection Requirements
Organize by control type:
**Technical Controls**
**Process Controls**
**Monitoring Controls**

### Compliance Actions
Prioritize recommendations:
1️⃣ **Critical Actions** - Immediate attention required
2️⃣ **Important Steps** - Near-term implementation
3️⃣ **Best Practices** - Long-term improvements

Use clear headings and bullet points for visual organization.
Highlight critical findings in **bold**.
Maintain consistent formatting throughout the analysis.

Include -> *Contact info@datainfa.com for futher understaing and DPDP implementation*
"""

def get_ai_analysis(schema: str) -> Optional[Dict]:
    """Get AI analysis of database schema using OpenRouter with DeepSeek"""
    logger.info("Starting AI analysis of database schema")
    try:
        api_key = config.get_ai_api_key()
        if not api_key:
            logger.error("API key not found in configuration")
            raise ValueError("API key not found in configuration")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://datainfa.com",
                "X-Title": "Compliance Assessment Tool",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {"role": "system", "content": "You are a DPDP compliance expert analyzing database schemas."},
                    {"role": "user", "content": SENSITIVE_DATA_PROMPT.format(schema=schema)}
                ],
                "temperature": 0.1,
                "max_tokens": 8000
            }
        )

        if response.status_code != 200:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return None

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        return None

def parse_ai_response(response: str) -> Dict:
    """Parse AI response into structured sections"""
    logger.info("Starting to parse AI response")
    
    structured_data = {
        "sensitive_fields": {
            "Personal Identifiers": [],
            "Financial Information": [],
            "Health-Related Data": [],
            "Biometric/Genetic Data": [],
            "Digital/Online Identifiers": [],
            "Location Information": [],
            "Employment Information": []
        },
        "recommendations": [],
        "protection_measures": []
    }
    
    # Clean category names mapping
    category_mapping = {
        "personal identifiers": "Personal Identifiers",
        "financial information": "Financial Information",
        "health-related data": "Health-Related Data",
        "biometric/genetic data": "Biometric/Genetic Data",
        "digital/online identifiers": "Digital/Online Identifiers",
        "location information": "Location Information",
        "employment information": "Employment Information"
    }
    
    current_section = None
    current_category = None
    
    def extract_risk_level(text: str) -> Tuple[str, str]:
        """Helper function to extract field and risk level from text"""
        text = text.strip()
        field = text
        risk = "Unknown"
        
        # Common risk indicators in the text
        risk_patterns = {
            "high": ["high risk:", "high risk -", "(high risk)", "high:"],
            "medium": ["medium risk:", "medium risk -", "(medium risk)", "medium:"],
            "low": ["low risk:", "low risk -", "(low risk)", "low:"]
        }
        
        # First try the explicit " - " separator
        if " - " in text:
            field, risk = text.rsplit(" - ", 1)
            return field.strip(), risk.strip()
            
        # Then try pattern matching
        lower_text = text.lower()
        for level, patterns in risk_patterns.items():
            for pattern in patterns:
                if pattern in lower_text:
                    # Remove the risk pattern from the field text
                    field = text.lower().replace(pattern, "").strip()
                    return field, level.title()
                    
        # Check for risk level at start of line
        for level in ["High", "Medium", "Low"]:
            if text.startswith(f"{level} Risk:"):
                field = text[len(f"{level} Risk:"):].strip()
                return field, level
                
        return field, risk
    
    def determine_risk_level(text: str) -> str:
        """Helper function to determine risk level from field description"""
        text = text.lower()
        
        # High risk indicators
        high_risk_patterns = [
            "direct pii", "unique identifier", "personal contact",
            "physical address", "salary data", "income data",
            "authentication", "personal information"
        ]
        
        # Medium risk indicators
        medium_risk_patterns = [
            "indirect", "could link", "could identify",
            "geographical", "tracking", "timeline",
            "performance data", "organizational"
        ]
        
        # Low risk indicators
        low_risk_patterns = [
            "public", "generic", "non-sensitive",
            "directory", "general"
        ]
        
        # Check for explicit risk mentions first
        if any(phrase in text for phrase in ["high risk", "critical", "sensitive"]):
            return "High Risk"
        elif any(phrase in text for phrase in ["medium risk", "moderate"]):
            return "Medium Risk"
        elif any(phrase in text for phrase in ["low risk", "minimal"]):
            return "Low Risk"
            
        # Then check content patterns
        if any(pattern in text for pattern in high_risk_patterns):
            return "High Risk"
        elif any(pattern in text for pattern in medium_risk_patterns):
            return "Medium Risk"
        elif any(pattern in text for pattern in low_risk_patterns):
            return "Low Risk"
            
        return "Medium Risk"  # Default to Medium if unclear

    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Clean line from markdown formatting
        clean_line = line.replace('*', '').replace('#', '').strip()
        
        # Detect main sections
        if "SENSITIVE FIELDS BY CATEGORY" in line.upper():
            current_section = "sensitive_fields"
            continue
        elif "COMPLIANCE RECOMMENDATIONS" in line.upper():
            current_section = "recommendations"
            continue
        elif "PROTECTION MEASURES" in line.upper():
            current_section = "protection_measures"
            continue
            
        # Check for category headers - now handles markdown formatting
        if any(cat.lower() in clean_line.lower() for cat in category_mapping.values()):
            # Extract category name from line
            for raw_cat, clean_cat in category_mapping.items():
                if raw_cat in clean_line.lower():
                    current_category = clean_cat
                    break
            continue
            
        # Process content based on section
        if line.startswith(('-', '•', '*')) or (clean_line.startswith(('-', '•', '*'))):
            cleaned_line = clean_line.lstrip('-•* ').strip()
            
            if current_section == "sensitive_fields" and current_category in structured_data["sensitive_fields"]:
                # Skip "None" or "Not Present" entries
                if any(skip in cleaned_line.lower() for skip in ["none", "not present", "no explicit"]):
                    continue
                    
                # Extract field name and description
                if "(" in cleaned_line:
                    field_name, description = cleaned_line.split("(", 1)
                    description = description.rstrip(")").strip()
                else:
                    field_name = cleaned_line
                    description = ""
                
                # Determine risk level from description
                risk_level = determine_risk_level(description or field_name)
                
                item = {
                    "field": field_name.strip(),
                    "risk": risk_level,
                    "description": description
                }
                structured_data["sensitive_fields"][current_category].append(item)
                
            elif current_section == "recommendations":
                structured_data["recommendations"].append(cleaned_line)
                
            elif current_section == "protection_measures":
                structured_data["protection_measures"].append(cleaned_line)
    
    return structured_data

def analyze_ddl_script(ddl_content: str) -> Dict:
    """Analyze DDL script using AI for DPDP-sensitive data"""
    logger.info("Starting DDL script analysis")
    
    try:
        statements = sqlparse.parse(ddl_content)
        if not statements:
            return {"error": "No valid SQL statements found"}
            
        schema_text = ""
        create_count = 0
        extracted_fields = []
        
        # Extract field names and types from CREATE statements
        for statement in statements:
            if statement.get_type() == 'CREATE':
                create_count += 1
                schema_text += str(statement) + "\n\n"
                
                # Parse fields from CREATE TABLE statement
                for token in statement.tokens:
                    if isinstance(token, sqlparse.sql.Parenthesis):
                        field_definitions = token.value.strip('()').split(',')
                        for field_def in field_definitions:
                            field_def = field_def.strip()
                            if field_def and not field_def.startswith(('PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT')):
                                field_parts = field_def.split()
                                if field_parts:
                                    field_name = field_parts[0]
                                    field_type = field_parts[1] if len(field_parts) > 1 else 'unknown'
                                    extracted_fields.append({
                                        'name': field_name,
                                        'type': field_type
                                    })
        
        if not schema_text:
            return {"error": "No CREATE TABLE statements found"}
            
        # Add extracted fields to the prompt with emphasis on categorization
        enhanced_prompt = SENSITIVE_DATA_PROMPT.format(
            schema=f"""
Database Schema:
{schema_text}

Extracted Fields for Analysis:
{'-' * 40}
{chr(10).join([f'• {f["name"]} ({f["type"]})' for f in extracted_fields])}
{'-' * 40}

Please analyze these fields and categorize them according to the DPDP categories above.
For each field, indicate the risk level (High/Medium/Low) based on sensitivity.
"""
        )
        
        logger.info(f"Analyzing {len(extracted_fields)} fields")
        
        # Get raw AI analysis first
        raw_analysis = get_ai_analysis(enhanced_prompt)
        if not raw_analysis:
            return {"error": "AI analysis failed"}
        
        # Store both raw and structured formats
        structured_analysis = parse_ai_response(raw_analysis)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "schema_analyzed": schema_text,
            "extracted_fields": extracted_fields,
            "findings": structured_analysis["sensitive_fields"],
            "recommendations": structured_analysis["recommendations"],
            "protection_measures": structured_analysis["protection_measures"],
            "raw_analysis": raw_analysis  # Include raw LLM output
        }
            
    except Exception as e:
        logger.error(f"Schema analysis error: {str(e)}")
        return {"error": str(e)}

def get_recommendations(findings: Dict) -> List[str]:
    """Get recommendations from AI analysis"""
    logger.info("Generating recommendations from findings")
    
    if "error" in findings:
        return [f"Error: {findings['error']}"]
        
    try:
        recommendations = []
        
        # Add general recommendations
        recommendations.append("General Data Protection Recommendations:")
        recommendations.append("Implement data encryption at rest and in transit")
        recommendations.append("Set up access controls and audit logging")
        recommendations.append("Establish data retention and deletion policies")
        
        # Add AI-generated recommendations if available
        if findings.get("recommendations"):
            recommendations.append("\n🤖 AI-Generated Specific Recommendations:")
            for rec in findings["recommendations"]:
                recommendations.append(f"• {rec}")
                
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation generation error: {str(e)}")
        # Return basic recommendations instead of error
        return [
            "Implement encryption for sensitive data",
            "Set up access controls and monitoring",
            "Create data handling policies",
            "Regularly review and update security measures"
        ]

def render_findings_section(findings: Dict) -> None:
    """Render the findings section with proper formatting"""
    if not findings:
        logger.warning("No findings to display")
        st.info("No sensitive data patterns found in the analysis.")
        return

    # Add CSS for risk level colors
    st.markdown("""
        <style>
        .high-risk { color: #FF4B4B; }
        .medium-risk { color: #FFA500; }
        .low-risk { color: #00CC96; }
        .unknown-risk { color: #A0A0A0; }
        </style>
    """, unsafe_allow_html=True)
    
    # If raw analysis is available, render it directly
    if "raw_analysis" in findings:
        # Clean the raw analysis text
        analysis_text = findings["raw_analysis"]
        analysis_text = analysis_text.replace("```markdown", "").replace("```", "")
        analysis_text = analysis_text.replace("<div>", "").replace("</div>", "")
        
        # Render cleaned raw analysis text
        st.markdown(analysis_text)
        return
        
    # Fall back to structured display if no raw analysis
    st.subheader("Analysis Results")
    
    st.subheader("Sensitive Data Fields by Category")
    
    # Initialize counters
    total_fields = 0
    categories_with_data = 0
    risk_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    
    # Count fields and risks
    for category, items in findings.items():
        if items and isinstance(items, list):
            total_fields += len(items)
            if len(items) > 0:
                categories_with_data += 1
            
            for item in items:
                if isinstance(item, dict):
                    risk = item.get("risk", "unknown").lower()
                    # More specific risk level detection
                    if any(high in risk.lower() for high in ["high", "critical", "severe"]):
                        risk_counts["high"] += 1
                    elif any(med in risk.lower() for med in ["medium", "moderate"]):
                        risk_counts["medium"] += 1
                    elif any(low in risk.lower() for low in ["low", "minimal"]):
                        risk_counts["low"] += 1
                    else:
                        risk_counts["unknown"] += 1
    
    # Display summary stats
    st.info(f"Found {total_fields} sensitive fields across {categories_with_data} categories")
    
    # Display findings by category
    for category, items in findings.items():
        if items and isinstance(items, list) and len(items) > 0:
            with st.expander(f"{category} ({len(items)} fields)", expanded=True):
                # Filter out "Not Applicable" and empty entries
                filtered_items = [
                    item for item in items 
                    if isinstance(item, dict) and 
                    item.get('field', '').strip() and  # Check for non-empty field
                    not any(na in item.get('field', '').lower() for na in 
                          ['not applicable', 'none', 'not present'])
                ]
                
                # Sort items by risk level
                high_risk = [item for item in filtered_items if isinstance(item, dict) and "high" in item.get("risk", "").lower()]
                medium_risk = [item for item in filtered_items if isinstance(item, dict) and "medium" in item.get("risk", "").lower()]
                low_risk = [item for item in filtered_items if isinstance(item, dict) and "low" in item.get("risk", "").lower()]
                other_risk = [item for item in filtered_items if isinstance(item, dict) and 
                            not any(level in item.get("risk", "").lower() for level in ["high", "medium", "low"])]
                
                def clean_field_text(field_text: str) -> str:
                    """Clean field text for display"""
                    # Remove risk level text
                    field_text = field_text.replace("High Risk:", "").replace("Medium Risk:", "").replace("Low Risk:", "")
                    field_text = field_text.replace("- High Risk", "").replace("- Medium Risk", "").replace("- Low Risk", "")
                    # Remove backticks and extra spaces
                    field_text = field_text.replace("`", "").strip()
                    # Remove any empty bullet points
                    field_text = field_text.replace("• ", "").strip()
