"""
Natural Language Generation module for creating well-formatted human-readable reports.
Supports template-based reports and optional integration with external AI APIs.
Returns properly formatted reports with headings, bullet points, sections, and paragraphs.
"""

from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
import time
import re
import os

import config

logger = logging.getLogger(__name__)

# Constants for different report tones
TONE_POSITIVE = "positive"
TONE_NEUTRAL = "neutral"
TONE_CONCERNED = "concerned"

# Define report format options
FORMAT_MARKDOWN = "markdown"
FORMAT_HTML = "html"
FORMAT_PLAIN = "plain"

def generate_report(results: Dict[str, Any], use_external_api: bool = True, format: str = FORMAT_MARKDOWN) -> str:
    """
    Generate a formatted report based on assessment results
    
    Args:
        results: Assessment results dictionary
        use_external_api: Whether to use an external AI API for enhanced report generation
        format: Output format (markdown, html, or plain)
        
    Returns:
        String containing the formatted report
    """
    # Log the start of report generation
    # logger.info(f"Starting report generation process in {format} format")
    
    # Get AI configuration status and log it
    ai_enabled = _is_api_configured()
    # logger.info(f"AI API configuration status: enabled={ai_enabled}, use_external_api={use_external_api}")
    
    if use_external_api and ai_enabled:
        try:
            # logger.info(f"Attempting AI-powered report generation using {config.get_ai_provider()} API")
            start_time = time.time()
            report = _generate_report_with_api(results, format)
            duration = time.time() - start_time
            # logger.info(f"Successfully generated AI report in {duration:.2f} seconds")
            return report
        except Exception as e:
            logger.error(f"Error using external API for report generation: {str(e)}", exc_info=True)
            # logger.info("Falling back to template-based report")
    else:
        if use_external_api:
            if not ai_enabled:
                logger.warning("External API requested but not configured, using template-based report generation")
            else:
                # logger.info("External API configured but not requested, using template-based report generation")
                pass
        else:
            # logger.info("Using template-based report generation as requested")
            pass
    
    # Default to template-based report
    # logger.info(f"Generating template-based report in {format} format")
    start_time = time.time()
    report = _generate_template_report(results, format)
    
    if not report:
        error_msg = "Error generating report. Please try again or contact support."
        logger.error("Template report generation failed")
        return error_msg
        
    duration = time.time() - start_time
    # logger.info(f"Generated template-based report in {duration:.2f} seconds")
    return report

def _generate_template_report(results: Dict[str, Any], format: str = FORMAT_MARKDOWN) -> str:
    """Generate formatted report using templates and rules"""
    try:
        # Extract key information from the results
        overall_score = results.get("overall_score", 0)
        section_scores = results.get("section_scores", {})
        compliance_level = results.get("compliance_level", "Unknown")
        recommendations = results.get("recommendations", {})
        
        # Determine overall tone based on score
        if overall_score >= 80:
            tone = TONE_POSITIVE
            overall_assessment = "Your organization demonstrates strong compliance with the data protection requirements."
        elif overall_score >= 60:
            tone = TONE_NEUTRAL
            overall_assessment = "Your organization shows moderate compliance with data protection requirements, but there are areas that need improvement."
        else:
            tone = TONE_CONCERNED
            overall_assessment = "Your organization has significant compliance gaps that should be addressed urgently."

        # Generate markdown report
        md_report = []
        
        # Report header with markdown formatting
        md_report.extend([

            "## EXECUTIVE SUMMARY",
            "",
            f"Based on the assessment, your organization's overall compliance score is **{overall_score:.1f}%**, "
            f"which indicates a **{compliance_level}** level of compliance.",
            "",
            f"{overall_assessment}",
            "",
            "## DETAILED FINDINGS",
            ""
        ])
        
        

        # Sort sections by their scores (ascending) to highlight most critical areas first
        sorted_sections = sorted(section_scores.items(), key=lambda x: x[1] if x[1] is not None else 1.0)
        
        for section, score in sorted_sections:
            if score is None:
                continue
            
            score_percentage = score * 100
            section_recommendations = recommendations.get(section, [])
            
            if score_percentage < 60:
                risk_level = "HIGH RISK"
                action_urgency = "urgent attention"
            elif score_percentage < 75:
                risk_level = "MODERATE RISK"
                action_urgency = "attention"
            else:
                risk_level = "LOW RISK"
                action_urgency = "continued monitoring"
            
            md_report.append(f"### {section} - {score_percentage:.1f}%")
            md_report.append(f"**Risk Level: {risk_level}**")
            md_report.append(f"This area requires {action_urgency}.")
            
            if section_recommendations:
                md_report.append("#### Key recommendations:")
                for rec in section_recommendations[:3]:  # Show at most 3 recommendations
                    md_report.append(f"* {rec}")
                
                if len(section_recommendations) > 3:
                    md_report.append(f"* *And {len(section_recommendations) - 3} more recommendation(s).*")
            
            md_report.append("")
        
        md_report.append("## ACTION PLAN")
        md_report.append("")

        if overall_score < 60:
            md_report.append("**Given the high-risk areas identified, we recommend the following priority actions:**")
        elif overall_score < 75:
            md_report.append("**To improve your compliance posture, consider the following actions:**")
        else:
            md_report.append("**To maintain your strong compliance posture, consider the following actions:**")
        
        md_report.append("")
        
        # Identify top priority areas (lowest scores)
        priority_sections = sorted(
            [(section, score) for section, score in section_scores.items() if score is not None], 
            key=lambda x: x[1]
        )[:3]
        
        for i, (section, _) in enumerate(priority_sections, 1):
            section_recommendations = recommendations.get(section, [])
            if section_recommendations and len(section_recommendations) > 0:
                md_report.append(f"{i}. **Focus on improving {section}** by implementing these actions:")
                for j, rec in enumerate(section_recommendations[:2], 1):
                    md_report.append(f"   {j}. {rec}")
                md_report.append("")

        # Join the report lines with newlines
        return "\n".join(md_report)
        
    except Exception as e:
        logger.error(f"Template report generation failed: {e}")
        return "Error: Unable to generate compliance report. Please try again or contact support."

def _generate_report_with_api(results: Dict[str, Any], format: str = FORMAT_MARKDOWN) -> str:
    """Generate a formatted report using external AI API"""
    api_key = config.get_ai_api_key()
    api_type = config.get_ai_provider()
    
    if not api_key:
        logger.warning("API key not found, falling back to template report")
        return _generate_template_report(results, format)
    
    # Prepare context for the AI
    # logger.info(f"Preparing context data for {api_type} API")
    context = _prepare_ai_context(results)
    
    # Handle different API providers
    if api_type == "openrouter":
        # logger.info(f"Using {api_type} API for report generation")
        # logger.info(f"Configuring {api_type} API client")
        report = _generate_with_openai(context, api_key, format, use_openrouter=True)
        # logger.info(f"{api_type} client configured with model: {config.get_ai_model()}")
    elif api_type == "azure":
        report = _generate_with_azure(context, api_key, format)
    else:
        report = _generate_with_openai(context, api_key, format)
    
    return report

def _prepare_ai_context(results: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare the context data for the AI model"""
    # Format the input data for the API
    overall_score = results.get("overall_score", 0)
    section_scores = results.get("section_scores", {})
    compliance_level = results.get("compliance_level", "Unknown")
    
    # Convert section scores to list format for better serialization
    section_data = []
    for section, score in section_scores.items():
        if score is not None:
            recommendations = results.get("recommendations", {}).get(section, [])
            section_data.append({
                "name": section,
                "score": score * 100,  # Convert to percentage
                "recommendations": recommendations[:3]  # Limit to top 3 recommendations
            })
    
    # Create the context object
    context = {
        "overall_score": overall_score,
        "compliance_level": compliance_level,
        "sections": section_data,
        "regulation": "Data Protection and Privacy Compliance"
    }
    
    return context

def _show_section_progress(section_number: int, total_sections: int = 13) -> None:
    """Display progress message for each section"""
    import streamlit as st
    import time
    
    if section_number <= total_sections:
        progress_text = f"🔄 Analyzing Section {section_number} of {total_sections}..."
        if not hasattr(_show_section_progress, 'progress_container'):
            _show_section_progress.progress_container = st.empty()
        _show_section_progress.progress_container.info(progress_text)
        time.sleep(3)  # Show each section for 3 seconds
    elif section_number == total_sections + 1:  # Show final message
        final_text = "✅ Analyzed all sections. Generating report..."
        _show_section_progress.progress_container.info(final_text)
        time.sleep(2)  # Show final message for 2 seconds

def _generate_with_openai(context: Dict[str, Any], api_key: str, format: str = FORMAT_MARKDOWN, use_openrouter: bool = False) -> str:
    """Generate a formatted report using OpenAI API through OpenRouter or directly"""
    if not api_key:
        logger.error("No API key provided")
        return _generate_template_report(context, format)

    try:
        from openai import OpenAI
        import httpx  # Add httpx import for timeout support
        import re  # Add re for HTML tag validation
        import streamlit as st
        import threading
        import queue
        
        # Create a queue to communicate between threads
        result_queue = queue.Queue()
        
        def generate_report_thread():
            try:
                if use_openrouter:
                    logger.info("Configuring OpenRouter API client")
                    # Remove SSL_CERT_FILE from environment if it exists
                    if 'SSL_CERT_FILE' in os.environ:
                        del os.environ['SSL_CERT_FILE']
                    
                    # Initialize OpenAI client with default SSL configuration
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                        default_headers={
                            "HTTP-Referer": "https://github.com/OpenRouter/",
                            "X-Title": "Compliance Assessment Tool"
                        }
                    )
                    model = "deepseek/deepseek-chat-v3-0324:free"
                    logger.info(f"OpenRouter client configured with model: {model}")
                    
                else:
                    logger.info("Configuring direct OpenAI API client")
                    client = OpenAI(api_key=api_key)
                    model = "gpt-4"
                    
                # Connection test commented out to save API credits
                # The initial check was commented out to avoid consuming API credits for verification.
                # Error handling around the main API call will now catch authentication/connection issues.
                # Uncomment the block below to re-enable the connection test.
                # try:
                #     response = client.chat.completions.create(
                #         model=model,
                #         messages=[
                #             {"role": "system", "content": "Verify authentication"},
                #             {"role": "user", "content": "Test"}
                #         ],
                #         max_tokens=5,
                #         timeout=5.0
                #     )
                #     logger.info("API authentication successful")
                # except Exception as auth_error:
                #     logger.error(f"API authentication failed: {str(auth_error)}")
                #     result_queue.put(_generate_template_report(context, format))
                #     return
                
                # Create the prompt based on requested format
                logger.info(f"Creating AI prompt for {format} format from context data")
                prompt = _create_openai_prompt(context, format)
                logger.info(f"Created prompt with length: {len(prompt)} characters")
                
                # Make the API request with retry logic
                max_retries = 3
                backoff_factor = 2
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        logger.info(f"Making API request attempt {retry_count + 1}/{max_retries}")
                        start_time = time.time()
                        
                        # Determine system prompt based on format
                        if format == FORMAT_MARKDOWN:
                            system_prompt = "You are an expert compliance analyst specializing in data protection regulations. Create a professional compliance report based on the assessment results provided. Format your response using Markdown for clear structure with headings, bullet points, and emphasized text. Use proper Markdown formatting for all structural elements."
                        elif format == FORMAT_HTML:
                            system_prompt = "You are an expert compliance analyst specializing in data protection regulations. Create a professional compliance report based on the assessment results provided. Format your response using HTML for proper structure with headings, paragraphs, lists, and emphasized text. Include appropriate HTML tags for all structural elements."
                        else:  # FORMAT_PLAIN
                            system_prompt = "You are an expert compliance analyst specializing in data protection regulations. Create a professional compliance report based on the assessment results provided. Return a plain text report with clear section titles, indentation, and structural elements to ensure readability without special formatting."
                        
                        # Build request parameters
                        request_params = {
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1,
                            "max_tokens": 8000,
                            "timeout": 30.0
                        }
                        
                        if use_openrouter:
                            request_params["extra_headers"] = {
                                "HTTP-Referer": "https://datainfa.com",
                                "X-Title": "Compliance Assessment Tool"
                            }
                        
                        # Make the API call
                        logger.info(f"Sending request to {'OpenRouter' if use_openrouter else 'OpenAI'} API")
                        response = client.chat.completions.create(**request_params)
                        
                        # Log the full response object for debugging
                        try:
                            response_json = response.model_dump_json(indent=2)
                            logger.info(f"Received full API response")
                        except Exception as log_err:
                            logger.error(f"Error logging full API response: {log_err}")
                            logger.info(f"Received raw response object: {response}")

                        duration = time.time() - start_time
                        logger.info(f"API call completed successfully in {duration:.2f} seconds")
                        
                        if hasattr(response, 'choices') and response.choices:
                            report_content = response.choices[0].message.content
                            if report_content:
                                logger.info(f"Received valid response with content length: {len(report_content)} characters")
                                if format == FORMAT_HTML:
                                    # Check for stray closing tags
                                    stray_tags = re.findall(r'</[^>]*>', report_content)
                                    opening_tags = re.findall(r'<[^/][^>]*>', report_content)
                                    closing_tags = [tag[2:-1] for tag in stray_tags]
                                    opening_tags = [re.sub(r'\s.*', '', tag[1:-1]) for tag in opening_tags]
                                    
                                    # Count opening and closing tags
                                    tag_count = {}
                                    for tag in opening_tags:
                                        tag_count[tag] = tag_count.get(tag, 0) + 1
                                    for tag in closing_tags:
                                        tag_count[tag] = tag_count.get(tag, 0) - 1
                                    
                                    # Check for mismatched tags
                                    mismatched_tags = {tag: count for tag, count in tag_count.items() if count != 0}
                                    if mismatched_tags:
                                        logger.warning(f"Found mismatched HTML tags: {mismatched_tags}")
                                        for tag in mismatched_tags:
                                            if mismatched_tags[tag] < 0:
                                                report_content = re.sub(f'</\\s*{tag}\\s*>', '', report_content)
                                                logger.info(f"Removed stray closing tag: </\\s*{tag}\\s*>")
                                result_queue.put(report_content)
                                return
                        
                        raise ValueError(f"Invalid response format: {response}")
                        
                    except httpx.TimeoutException:
                        logger.error(f"API request timed out (attempt {retry_count + 1}/{max_retries})")
                        retry_count += 1
                        if retry_count == max_retries:
                            logger.error("All API attempts timed out. Using template-based report as fallback.")
                            result_queue.put(_generate_template_report(context, format))
                            return
                        wait_time = backoff_factor ** retry_count
                        logger.warning(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"API request failed (attempt {retry_count}/{max_retries}): {str(e)}")
                        if retry_count == max_retries:
                            logger.error(f"Failed to generate report with API after {max_retries} attempts. Falling back to template.")
                            result_queue.put(_generate_template_report(context, format))
                            return
                        wait_time = backoff_factor ** retry_count
                        logger.warning(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                
                result_queue.put(_generate_template_report(context, format))
                
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {str(e)}", exc_info=True)
                result_queue.put(_generate_template_report(context, format))
        
        # Start the report generation in a separate thread
        report_thread = threading.Thread(target=generate_report_thread)
        report_thread.start()
        
        # Show progress while waiting for the report
        for section in range(1, 15):  # Show progress for sections 1-13 plus final message
            if not report_thread.is_alive():
                break  # Stop showing progress if report is ready
            _show_section_progress(section)
        
        # Clear the progress message when done
        if hasattr(_show_section_progress, 'progress_container'):
            _show_section_progress.progress_container.empty()
        
        # Wait for the report generation to complete
        report_thread.join()
        return result_queue.get()
        
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {str(e)}", exc_info=True)
        return _generate_template_report(context, format)

def _generate_with_azure(context: Dict[str, Any], api_key: str, format: str = FORMAT_MARKDOWN) -> str:
    """Generate a formatted report using Azure OpenAI API"""
    # Azure OpenAI implementation
    # This would be similar to the OpenAI implementation but with Azure endpoints
    # For now, we'll fall back to the template report
    logger.warning("Azure OpenAI integration not fully implemented yet")
    return _generate_template_report(context, format)

def _create_openai_prompt(context: Dict[str, Any], format: str = FORMAT_MARKDOWN) -> str:
    """Create a detailed prompt for the OpenAI API requesting properly formatted output"""
    overall_score = context["overall_score"]
    compliance_level = context["compliance_level"]
    sections = context["sections"]
    
    # Serialize the section data in a readable format
    sections_text = ""
    for section in sections:
        sections_text += f"\n- {section['name']}: {section['score']:.1f}% compliance"
        if section.get('recommendations'):
            sections_text += "\n  Key recommendations:"
            for i, rec in enumerate(section['recommendations'], 1):
                sections_text += f"\n  {i}. {rec}"
    
    # Determine format-specific instructions
    if format == FORMAT_MARKDOWN:
        format_instructions = """
Please format the report using proper Markdown:
- Use # for top-level headings, ## for second-level, etc.
- Use **bold** for emphasis and important information
- Use bullet points (*) for lists of items
- Use numbered lists (1. 2. 3.) for sequential steps or priorities
- Use horizontal rules (---) to separate major sections if needed
- Include appropriate paragraph breaks for readability
- DO NOT include any HTML tags in the output

IMPORTANT: Return ONLY the Markdown formatted report without ANY explanatory text or HTML tags.
"""
    elif format == FORMAT_HTML:
        format_instructions = """
Please format the report using proper HTML:
- Use <h1>, <h2>, <h3> tags for headings of different levels
- Use <strong> or <b> tags for emphasis and important information
- Use <ul> and <li> tags for bullet point lists
- Use <ol> and <li> tags for numbered lists
- Use <p> tags for paragraphs with appropriate spacing
- Use <hr> tags to separate major sections if needed
- Use <div> tags sparingly and ONLY when necessary for layout
- Ensure all HTML tags are properly closed in the correct order
- DO NOT include any stray or unnecessary closing tags
- Validate that each opening tag has exactly one matching closing tag

IMPORTANT: Return ONLY the HTML formatted report with properly balanced HTML tags. Do not include any stray closing tags.
"""
    else:  # FORMAT_PLAIN
        format_instructions = """
Please format the report in a structured plain text format:
- Use UPPERCASE and line separators (====) for main headings
- Use title case and line separators (----) for subheadings
- Use indentation with spaces for hierarchical structure
- Use symbols like * or - for bullet points
- Use clearly numbered items for sequential steps or priorities
- Include blank lines between sections for readability
- Use simple text emphasis like UPPERCASE or *asterisks* for important points
- DO NOT include any HTML tags

IMPORTANT: Return ONLY the plaintext formatted report without ANY explanatory text or HTML tags.
"""
    
    prompt = f"""
Generate a detailed compliance report based on the following assessment results:

Overall Compliance Score: {overall_score:.1f}%
Compliance Level: {compliance_level}

Section Scores and Recommendations:{sections_text}

Information for your report on what products you can recommend based on the results:
"1. Data gets Collected

2. Data is discovered
Discover Digital Personal Data.
Identify Digital Personal Data Estate.
Comply with data minimization, process limitation, and storage limitations.
Relevant Informatica Products: Informatica Cloud Data Governance (CDGC), Metadata Command Center (MCC), Informatica Cloud Data Profiling (CDP), Informatica Data Privacy Management (DPM)

3. Data is labeled based on sensitivity and protection needs
Keep track of digital personal data.
Respond to data principal access rights.
Maintain accuracy and correctness.
Keep track of personal data of children.
Appropriately protect data.
Relevant Informatica Products: Informatica Cloud Data Governance (CDGC), Informatica Cloud Data Quality (CDQ), Informatica Cloud Data Validation (CDV), Informatica Cloud Data Integration (CDI)

4. Data gets protected based on policies
Safeguard personal data.
Protect personal data from unauthorized processing.
Track personal data.
Relevant Informatica Products: Informatica Data Privacy Management (DPM), Informatica Cloud Data Access Management (CDAM), Informatica Cloud Data Governance (CDGC)

5(a). Data Travel Across National Boundaries
Close monitoring of data transfers.
Location-based policies to restrict access from unauthorized locations.
Relevant Informatica Products: Informatica Cloud Data Governance Catalog (CDGC), Informatica Cloud Data Privacy Management (CDPM), Informatica Cloud Data Access Management (CDAM)

5(b). Personal data is processed
Adherence to data minimization and remediation of data exposure.
Track processing activity to ensure lawful and fair processing.
Manage Data Principal Rights.
Relevant Informatica Products: Informatica Cloud Data Quality (CDQ), Informatica Cloud Data Privacy Management (CDPM), Informatica Cloud Data Governance (CDGC)

5(c). Data activity is monitored
Detect and respond to unauthorized access, transfer, or processing activities on personal data.
Relevant Informatica Products: Informatica Cloud Application Integration (CAI), Informatica Cloud Data Governance Catalog (CDGC), CLAIRE GPT

6. Data gets retired and deleted
Retention and data lifecycle management.
Mark documents as "Records".
Disposition reviews to mark safe deletion.
Relevant Informatica Products: Informatica Cloud Data Integration (CDI), Informatica Cloud Data Quality (CDQ), Informatica Cloud Master Data Management (CMDM), Informatica Cloud Data Access Management (CDAM)."



Your report should include:
1. An executive summary assessing the overall compliance status
2. Analysis of each section with risk levels and implications
3. Prioritized action items with clear descriptions
4. Strategic recommendations for improving compliance posture (focus on Informatica Solutions provided in the context)

IMPORTANT FORMATTING INSTRUCTIONS:
- DO NOT prefix recommendations with "Informatica Solution:"
- Present recommendations directly and concisely
- When mentioning Informatica products, integrate them naturally into the recommendations

{format_instructions}

Ensure the tone is professional but accessible, avoiding overly technical language.
Use data-driven insights to provide specific, actionable recommendations.
Include at the end -> Partner with Informatica experts to close gaps efficiently.
Contact info@datainfa.com for further understanding and implementation.

IMPORTANT: Ensure all HTML tags are properly balanced and there are no stray closing tags in the output.
"""
    
    return prompt

def _is_api_configured() -> bool:
    """Check if external AI API is configured"""
    # logger.info("Checking AI API configuration")
    
    # Update to use direct properties instead of function calls if they exist
    # Otherwise, fall back to the function calls for compatibility
    ai_enabled = getattr(config, "AI_ENABLED", None)
    if ai_enabled is None:
        try:
            ai_enabled = config.get_ai_enabled()
            # logger.info(f"Got AI_ENABLED via function: {ai_enabled}")
        except AttributeError:
            # logger.warning("Could not find AI_ENABLED property or function, defaulting to False")
            ai_enabled = False
            
    ai_api_key = getattr(config, "AI_API_KEY", None)
    if ai_api_key is None:
        try:
            ai_api_key = config.get_ai_api_key()
            # logger.info(f"Got AI_API_KEY via function, length: {len(ai_api_key) if ai_api_key else 0}")
            # if ai_api_key:
            #     logger.info(f"API Key last 4 chars: {ai_api_key[-4:]}")
        except AttributeError:
            # logger.warning("Could not find AI_API_KEY property or function")
            ai_api_key = None
    # else:
    #     logger.info(f"Got AI_API_KEY directly, length: {len(ai_api_key) if ai_api_key else 0}")
    #     if ai_api_key:
    #         logger.info(f"API Key last 4 chars: {ai_api_key[-4:]}")
    
    # Log detailed configuration status
    if ai_enabled and ai_api_key:
        logger.info("AI API is fully configured and enabled")
        # logger.info(f"API key first 4 chars: {ai_api_key[:4] if ai_api_key and len(ai_api_key) > 4 else 'N/A'}")
        return True
    elif not ai_enabled:
        # logger.info("AI API is disabled in configuration")
        return False
    elif not ai_api_key:
        logger.warning("AI API is enabled but no API key is available")
        return False
    
    return False