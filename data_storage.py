"""Data storage module for the Compliance Assessment Tool.

This module handles persistent storage of assessment data including:
- Organization details
- Assessment responses
- Compliance reports
- Historical tracking
"""

import os
import json
from datetime import datetime
import logging
import pandas as pd
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from config import BASE_DIR

# Setup logging
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = os.path.join(BASE_DIR, "data")
ORG_DATA_DIR = os.path.join(DATA_DIR, 'organizations')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

# Email configuration with fallback values
try:
    email_secrets = st.secrets["email"]
    SMTP_SERVER = email_secrets.get("smtp_server", "smtp.gmail.com")
    SMTP_PORT = email_secrets.get("smtp_port", 587)
    SENDER_EMAIL = email_secrets.get("sender_email", "")
    SENDER_PASSWORD = email_secrets.get("sender_password", "")
    RECIPIENT_EMAIL = email_secrets.get("recipient_email", "")
except (KeyError, AttributeError) as e:
    logger.warning(f"Could not access email configuration from secrets: {e}")
    # Use default values
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = ""
    SENDER_PASSWORD = ""
    RECIPIENT_EMAIL = ""

def send_assessment_notification(org_name: str) -> bool:
    """Send email notification when a new assessment starts
    
    Args:
        org_name: Name of the organization starting the assessment
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # # Log configuration status
        # logger.info("Checking email configuration...")
        # logger.info(f"SMTP Server: {SMTP_SERVER}")
        # logger.info(f"SMTP Port: {SMTP_PORT}")
        # logger.info(f"Sender Email: {SENDER_EMAIL}")
        # logger.info(f"Recipient Email: {RECIPIENT_EMAIL}")
        
        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
            missing = []
            if not SENDER_EMAIL: missing.append("sender_email")
            if not SENDER_PASSWORD: missing.append("sender_password")
            if not RECIPIENT_EMAIL: missing.append("recipient_email")
            logger.error(f"Email notification skipped: Missing required configuration: {', '.join(missing)}")
            return False
            
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"New DPDP Assessment Started - {org_name}"
        
        # Create email body
        body = f"""
        A new DPDP compliance assessment has been started:
        
        Organization: {org_name}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        This is an automated notification from the DPDP Compliance Assessment Tool.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email with detailed logging
        logger.info("Attempting to connect to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # logger.info("Connected to SMTP server")
            
            # logger.info("Starting TLS connection...")
            server.starttls()
            # logger.info("TLS connection established")
            
            # logger.info("Attempting to authenticate...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # logger.info("Authentication successful")
            
            # logger.info("Sending email message...")
            server.send_message(msg)
            # logger.info("Email sent successfully")
            
        logger.info(f"Assessment notification email sent for {org_name}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        logger.error("Please check your email and password in secrets.toml")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending assessment notification email: {str(e)}")
        return False

def ensure_data_directories():
    """Ensure all necessary data directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ORG_DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def get_org_directory(org_name: str) -> str:
    """Get the directory path for an organization's data"""
    # Sanitize organization name for filesystem
    safe_name = ''.join(c for c in org_name if c.isalnum() or c in (' ', '-', '_')).strip()
    org_dir = os.path.join(ORG_DATA_DIR, safe_name)
    os.makedirs(org_dir, exist_ok=True)
    return org_dir

def save_assessment_data(data: Dict[str, Any]) -> bool:
    """Save assessment data for an organization
    
    Args:
        data: Dictionary containing assessment data including:
            - organization_name: Name of the organization
            - assessment_date: Date of assessment
            - selected_regulation: Selected regulation code
            - selected_industry: Selected industry code
            - responses: Assessment responses
            - results: Calculated results and recommendations
            - is_start: Boolean indicating if this is the start of assessment
            - is_complete: Boolean indicating if this is the completion of assessment
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        org_name = data.get('organization_name')
        if not org_name:
            logger.error("Organization name is required")
            return False
            
        # Debug logging for email triggers
        logger.info(f"Assessment data received - is_start: {data.get('is_start')}, is_complete: {data.get('is_complete')}")
            
        # Send notification email only at start
        if data.get('is_start', False):
            logger.info(f"Triggering start notification email for {org_name}")
            send_assessment_notification(org_name)
            
        # Get organization directory
        org_dir = get_org_directory(org_name)
        os.makedirs(org_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assessment_{timestamp}.json"
        filepath = os.path.join(org_dir, filename)
        
        # Add metadata
        save_data = data.copy()
        save_data['saved_at'] = datetime.now().isoformat()
        
        # Save assessment data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        
        # If assessment is complete, save and send report
        if data.get('is_complete', False) and data.get('results'):
            logger.info(f"Triggering completion report email for {org_name}")
            save_report(data)
            
        logger.info(f"Saved assessment data for {org_name} to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving assessment data: {e}")
        return False

def send_report_email(data: Dict[str, Any]) -> bool:
    """Send assessment report via email
    
    Args:
        data: Assessment data dictionary containing results
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        org_name = data['organization_name']
        assessment_date = data['assessment_date']
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"DPDP Assessment Report - {org_name}"
        
        # Create email body with report details
        body = f"""
        DPDP Compliance Assessment Report
        
        Organization: {org_name}
        Assessment Date: {assessment_date}
        Regulation: {data['selected_regulation']}
        Industry: {data['selected_industry']}
        
        Overall Score: {data['results']['overall_score']}%
        Compliance Level: {data['results']['compliance_level']}
        
        Section Scores:
        {chr(10).join(f"- {section}: {score*100}%" for section, score in data['results']['section_scores'].items() if score is not None)}
        
        Recommendations:
        {chr(10).join(f"- {section}: {chr(10)}  {chr(10).join('  - ' + rec for rec in recs)}" for section, recs in data['results']['recommendations'].items())}
        
        This is an automated report from the DPDP Compliance Assessment Tool.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email with detailed logging
        logger.info("Attempting to send assessment report email...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logger.info("Connected to SMTP server")
            server.starttls()
            logger.info("TLS connection established")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            logger.info("Authentication successful")
            server.send_message(msg)
            logger.info("Report email sent successfully")
            
        logger.info(f"Assessment report email sent for {org_name}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed while sending report: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred while sending report: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending assessment report email: {str(e)}")
        return False

def save_report(data: Dict[str, Any]) -> bool:
    """Save assessment report in multiple formats and send via email
    
    Args:
        data: Assessment data dictionary
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        org_name = data['organization_name']
        assessment_date = data['assessment_date']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"Starting report generation for {org_name}")
        
        # Get organization directory
        org_dir = get_org_directory(org_name)
        os.makedirs(org_dir, exist_ok=True)
        
        # Save JSON report
        json_path = os.path.join(org_dir, f"report_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data['results'], f, indent=2)
        
        # Save Excel report if pandas is available
        try:
            excel_path = os.path.join(org_dir, f"report_{timestamp}.xlsx")
            
            # Create Excel writer
            with pd.ExcelWriter(excel_path) as writer:
                # Overview sheet
                overview_data = {
                    'Organization': org_name,
                    'Assessment Date': assessment_date,
                    'Regulation': data['selected_regulation'],
                    'Industry': data['selected_industry'],
                    'Overall Score': data['results']['overall_score'],
                    'Compliance Level': data['results']['compliance_level']
                }
                pd.DataFrame([overview_data]).to_excel(writer, sheet_name='Overview', index=False)
                
                # Section scores
                scores_data = [
                    {'Section': section, 'Score': score * 100}
                    for section, score in data['results']['section_scores'].items()
                    if score is not None
                ]
                pd.DataFrame(scores_data).to_excel(writer, sheet_name='Section Scores', index=False)
                
                # Recommendations
                recs_data = []
                for section, recs in data['results']['recommendations'].items():
                    for rec in recs:
                        recs_data.append({'Section': section, 'Recommendation': rec})
                pd.DataFrame(recs_data).to_excel(writer, sheet_name='Recommendations', index=False)
        
        except Exception as e:
            logger.warning(f"Could not save Excel report: {e}")
        
        # Send report via email
        logger.info(f"Sending completion report email for {org_name}")
        send_report_email(data)
        
        logger.info(f"Saved and sent assessment report for {org_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving/sending report: {e}")
        return False

def get_organization_assessments(org_name: str) -> list:
    """Get list of all assessments for an organization
    
    Args:
        org_name: Name of the organization
    
    Returns:
        list: List of assessment data dictionaries, sorted by date
    """
    try:
        org_dir = get_org_directory(org_name)
        if not os.path.exists(org_dir):
            return []
            
        assessments = []
        for filename in os.listdir(org_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(org_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    assessment = json.load(f)
                    assessments.append(assessment)
        
        # Sort by assessment date
        assessments.sort(key=lambda x: x.get('assessment_date', ''), reverse=True)
        return assessments
        
    except Exception as e:
        logger.error(f"Error getting organization assessments: {e}")
        return []

def get_latest_assessment(org_name: str) -> Optional[Dict[str, Any]]:
    """Get the most recent assessment for an organization
    
    Args:
        org_name: Name of the organization
    
    Returns:
        Optional[Dict[str, Any]]: Latest assessment data or None if not found
    """
    assessments = get_organization_assessments(org_name)
    return assessments[0] if assessments else None

# Ensure data directories exist on module import
ensure_data_directories()