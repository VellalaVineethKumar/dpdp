"""
Centralized CSS styles for the Compliance Assessment Tool.

This module contains all CSS styling used throughout the application,
organized by component or page.
"""

def get_common_button_css():
    """Return the CSS for common button styling"""
    return """
        <style>
        /* Common button styles - Material UI inspired */
        button, .stButton>button {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: none !important;
            border-radius: 4px !important;
            text-align: left !important;
            padding: 0.5rem 0.75rem !important;  /* Reduced padding */
            font-size: 0.85rem !important;      /* Smaller font */
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24) !important;
            margin: 0.25rem 0 !important;      /* Reduced margin */
            width: 100% !important;
            min-height: 36px !important;       /* Material UI standard height */
            line-height: 1.2 !important;
            letter-spacing: 0.01em !important;
        }
        
        /* Hover state */
        button:hover:not(:disabled), .stButton>button:hover:not(:disabled) {
            background-color: #3b3b49 !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Active/Selected state */
        button:active, .stButton>button:active,
        button[data-testid="baseButton-secondary"] {
            background-color: #2b2d3a !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24) !important;
            transform: translateY(0) !important;
        }

        /* Primary button style */
        button[kind="primary"], .stButton>button[kind="primary"] {
            background-color: #2b2d3a !important;
            text-align: center !important;
            font-weight: 500 !important;
        }

        /* Secondary button style */
        button[kind="secondary"], .stButton>button[kind="secondary"] {
            background-color: #1e1e2d !important;
            text-align: center !important;
            opacity: 0.9 !important;
        }
        
        /* Special button styles (like print button) */
        button.special-button {
            background-color: #2b2d3a !important;
            text-align: center !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 1rem !important;
            letter-spacing: 0.02em !important;
        }
        
        /* Disabled state */
        button:disabled, .stButton>button:disabled {
            background-color: #1e1e1e !important;
            color: #666666 !important;
            box-shadow: none !important;
            cursor: not-allowed !important;
            opacity: 0.7 !important;
        }

        /* Container spacing for button groups */
        div.element-container {
            margin-bottom: 0.25rem !important;  /* Reduced margin between containers */
        }

        /* Fix Streamlit's default padding */
        .stButton {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Navigation panel specific styling */
        section[data-testid="stSidebarContent"] div.stButton button {
            background-color: #1e1e2d !important;
            color: #ffffff !important;
            margin: 0.15rem 0 !important;
            padding: 0.5rem 0.75rem !important;
            min-height: 32px !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
        }
        
        section[data-testid="stSidebarContent"] div.stButton button:hover {
            background-color: #2b2d3a !important;
            transform: translateX(2px) !important;
        }
        
        section[data-testid="stSidebarContent"] div.stButton button:active {
            background-color: #3b3b49 !important;
            transform: translateX(0) !important;
        }
        
        /* Compact input styling */
        div[data-testid="stTextInput"] input, 
        div.stSelectbox div[role="listbox"],
        div.stSelectbox div[role="option"] {
            padding: 0.25rem 0.5rem !important;
            min-height: 32px !important;
            font-size: 0.85rem !important;
        }
        
        /* Make select boxes more compact */
        .stSelectbox > div:first-child {
            min-height: 32px !important;
        }
        </style>
    """

def get_landing_page_css():
    """Return the CSS for the landing page"""
    return """
        <style>
        .main > div {
            padding: 1rem;
            max-width: 800px;
            margin: 0 auto;
        }
        /* Remove specific button styling and use common styles */
        .logo-container {
            text-align: center;
            padding: 2rem 0;
        }
        .logo-container img {
            max-width: 300px;  /* Increased from 75px to 300px */
            margin: 0 auto;
            display: block;
        }
        .title-container {
            text-align: center;
            margin-bottom: 2rem;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #888;
        }
        </style>
    """

def get_sidebar_css():
    """Return the CSS for the sidebar navigation"""
    return """
        <style>
            section[data-testid="stSidebar"] > div {
                padding-top: 1rem;
                background-color: #0e1117;
            }
            
            /* Logo container styling */
            section[data-testid="stSidebarContent"] div:has(> img) {
                text-align: center;
                padding: 1rem 0.5rem 2rem 0.5rem;
                margin: 0;
            }
            
            /* Logo image styling */
            section[data-testid="stSidebarContent"] img {
                width: 160px;
                display: block;
                margin: 0 auto;
            }
            
            /* Navigation buttons container */
            section[data-testid="stSidebarContent"] div.element-container {
                margin: 0.25rem 0;
            }
            
            /* Navigation buttons */
            section[data-testid="stSidebarContent"] .stButton > button {
                width: 100%;
                padding: 0.75rem 1rem;
                margin: 0.25rem 0;
                background-color: #1e1e2d !important;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                text-align: center;
                font-size: 0.9rem;
                transition: all 0.2s ease;
            }
            
            /* Button hover effect */
            section[data-testid="stSidebarContent"] .stButton > button:hover {
                background-color: #2b2d3a !important;
                transform: translateX(2px);
            }
        </style>
    """

def get_radio_button_css():
    """Return the CSS for enhanced radio buttons"""
    return """
        <style>
        div.row-widget.stRadio > div {
            flex-direction: column;
            gap: 10px;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            padding: 10px 15px;
            background: #262730;
            border: 1px solid #4e4e61;
            border-radius: 5px;
            width: 100%;
            transition: all 0.2s ease;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background: #3b3b49;
            border-color: #6e6e80;
            transform: translateY(-1px);
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label > div:first-child {
            margin-right: 10px;
        }
        /* Selected state */
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: #2b2d3a;
            border-color: #6fa8dc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        </style>
    """

def get_print_export_css():
    """Return the CSS for print/PDF export"""
    return """
    <style>
    @media print {
        header, footer, .stSidebar, .main .block-container > div:first-child, 
        button[kind="primary"], button[kind="secondary"], .reportview-container .main footer,
        .viewerBadge_container__1QSob, [data-testid="stToolbar"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        h1 {
            text-align: center;
            font-size: 1.5em !important;
        }
        @page {
            margin: 0.5cm;
        }
        body {
            print-color-adjust: exact !important;
            -webkit-print-color-adjust: exact !important;
        }
    }
    </style>
    """

def get_header_css():
    """Return the CSS for the application header"""
    return """
        <style>
        /* Reset all default spacing */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Compact header */
        .app-header {
            background: rgba(30, 30, 30, 0.8);
            padding: 0.4rem 0.5rem;
            border-radius: 4px;
            margin: 0 0 0.25rem 0;
        }
        
        .header-text {
            margin: 0;
            padding: 0;
        }
        
        .header-text h1 {
            color: white;
            font-size: 1.4rem;
            margin: 0;
            padding: 0;
            line-height: 1.1;
        }
        
        .header-text p {
            color: rgba(250, 250, 250, 0.8);
            font-size: 0.85rem;
            margin: 0.1rem 0 0 0;
            padding: 0;
            line-height: 1;
        }

        /* Remove Streamlit container spacing */
        div[data-testid="stMarkdown"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Hide empty containers */
        .element-container:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Remove top toolbar spacing */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Remove default header */
        [data-testid="stHeader"] {
            display: none !important;
        }

        /* Fix vertical block spacing */
        div[data-testid="stVerticalBlock"] > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
    """

def get_expiry_box_css():
    """Return the CSS for admin token expiry box styling"""
    return """
    <style>
    /* Fix alignment between input and display box */
    div[data-testid="column"] > div {
        display: flex;
        align-items: center;
        height: 100%;
    }
    /* Ensure the number input element is properly aligned */
    div[data-testid="stNumberInput"] {
        margin-bottom: 0 !important;
    }
    /* Style for the expiry box */
    .expiry-box {
        background-color: #262730;
        color: #ffffff;
        border-radius: 5px;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        height: 42px;
        box-sizing: border-box;
        margin-top: 23px; /* Match label height offset */
    }
    </style>
    """

# Update the print button HTML to use the special-button class
def get_print_button_html():
    """Return the HTML for the print button"""
    return """
    <div style="text-align: right; margin: 0.5rem 0;">
        <button 
            onclick="window.print()"
            class="special-button"
            style="padding: 8px 16px; font-size: 14px; margin: 4px 2px;"
        >
            📄 Export as PDF
        </button>
    </div>
    """

# Update section navigation to use common button styles
def get_section_navigation_css():
    """Return the CSS for the section navigation in dark theme"""
    return """
        <style>
        section[data-testid="stSidebarContent"] div.stExpander {
            background-color: transparent !important;
            border: none !important;
        }
        
        /* Dark background for the content area */
        section[data-testid="stSidebarContent"] div.stExpander > div[data-testid="stExpanderContent"] {
            background-color: #0e1117 !important;
            color: #fafafa !important;
            padding: 0 !important;
        }
        
        /* Remove default streamlit styling that causes white backgrounds */
        section[data-testid="stSidebarContent"] div.stExpander > div[data-testid="stExpanderContent"] p {
            color: #d1d1d1 !important;
            font-size: 0.9rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Navigation panel buttons will inherit styles from common button CSS */
        section[data-testid="stSidebarContent"] div.stButton button {
            background-color: #1e1e2d !important;
            border: none !important;
            margin: 0.25rem 0 !important;
            font-size: 0.9rem !important;
        }
        
        /* Hover effect */
        section[data-testid="stSidebarContent"] div.stButton button:hover:not(:disabled) {
            background-color: #2b2d3a !important;
            transform: translateX(2px) !important;
        }
        
        /* Fix any white backgrounds in the navigation panel */
        section[data-testid="stSidebarContent"] div,
        section[data-testid="stSidebarContent"] div.stExpander,
        section[data-testid="stSidebarContent"] div.stExpanderContent {
            background-color: transparent !important;
        }
        
        /* Caption text styling */
        section[data-testid="stSidebarContent"] div.stExpander .caption {
            color: #d1d1d1 !important;
            font-size: 0.85rem !important;
            margin-top: 0.75rem !important;
        }
        
        /* Style the expander itself to match dark theme */
        section[data-testid="stSidebarContent"] div.streamlit-expanderHeader {
            background-color: #262730 !important;
            color: white !important;
            border-radius: 4px !important;
        }
        
        /* Make sure all text in sidebar is light colored */
        section[data-testid="stSidebarContent"] div {
            color: #d1d1d1;
        }
        </style>
    """

def get_informatica_solution_css():
    """Return the CSS for Informatica solution styling"""
    return """
        <style>
        .informatica-solution {
            color: #FF4B4B !important;
            font-weight: bold;
        }
        .question-text a {
            color: #FF4B4B;
            text-decoration: none;
            border-bottom: 1px dashed #FF4B4B;
        }
        .question-text a:hover {
            color: #ff7575;
            border-bottom: 1px solid #ff7575;
        }
        </style>
    """

def get_section_header_css():
    """Return the CSS for section headers"""
    return """
        <style>
        /* Section header */
        .section-header {
            background: rgba(49, 51, 63, 0.08);
            padding: 0.4rem 0.75rem;
            border-radius: 4px;
            margin: 0.25rem 0;
        }
        
        .section-title {
            color: white;
            font-size: 1.2rem;
            margin: 0;
            padding: 0;
            line-height: 1.2;
        }

        /* Progress section */
        .progress-section {
            margin: 0.25rem 0;
            padding: 0;
            font-size: 0.85rem;
            opacity: 0.8;
        }

        /* Progress bar */
        .stProgress > div {
            margin: 0.15rem 0 !important;
            padding: 0 !important;
        }

        /* Question container */
        .question-container {
            margin-top: 0.5rem !important;
            padding: 0 !important;
        }

        /* Remove any stray margins */
        div[data-testid="stMarkdown"] > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
    """

def get_progress_metrics_css():
    """Return the CSS for progress metrics"""
    return """
        <style>
        .progress-metric {
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        </style>
    """

def get_penalties_table_css():
    """Return the CSS for penalties table"""
    return """
        <style>
        .penalties-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
            margin: 0.5em 0;
            background: #1E1E1E;
        }
        .penalties-table th:first-child,
        .penalties-table td:first-child {
            width: 40%;
            padding: 8px 10px;
        }
        .penalties-table th:nth-child(2),
        .penalties-table td:nth-child(2) {
            width: 40%;
            padding: 8px 10px;
            text-align: left;
        }
        .penalties-table th {
            background: ##ff7070;
            color: white;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #FF6B6B;
        }
        .penalties-table td {
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .penalties-table tr:hover td {
            background-color: rgba(255, 75, 75, 0.05);
        }
        .penalties-table tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02);
        }
        .penalties-note {
            background-color: rgba(255, 75, 75, 0.1);
            border-left: 3px solid #ff9090;
            padding: 8px 12px;
            margin-top: 10px;
            border-radius: 0 4px 4px 0;
            font-size: 0.85em;
            color: #FFF;
        }
        </style>
    """

def get_discovery_button_css():
    """Return the CSS for discovery button"""
    return """
        <style>
        .discovery-button {
            background-color: #4B4BFF;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .discovery-button:hover {
            background-color: #3A3AFF;
        }
        </style>
    """

def get_faq_css():
    """Return the CSS for FAQ page"""
    return """
        <style>
        .faq-header {
            color: #FF4B4B;
            margin-bottom: 2rem;
        }
        .faq-category {
            color: #FFA500;
            margin-top: 2rem;
        }
        .faq-question {
            color: #ffffff;
            background-color: #2E2E2E;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """

def get_input_label_css():
    """Return the CSS for input labels, now with white color for all labels."""
    return """
        <style>
        .input-label {
            font-size: 1rem;
            color: #fff !important;
            margin-bottom: 0.2rem;
        }
        label[data-testid="stWidgetLabel"],
        label,
        .stSelectbox label,
        .stTextInput label {
            color: #fff !important;
        }
        </style>
    """

def get_app_header_css():
    """Return the CSS for the application header"""
    return """
        <style>
        .app-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 5px;
        }
        .header-logo {
            width: 180px;
            height: auto;
        }
        .header-text {
            flex-grow: 1;
        }
        .header-text h1 {
            margin: 0;
            padding: 0;
            font-size: 1.8em;
        }
        .header-text p {
            margin: 2px 0 0 0;
            color: #cccccc;
            font-size: 0.9em;
        }
        </style>
    """

def get_contact_link_css():
    """Return the CSS for contact link"""
    return """
        <style>
        .contact-link {
            font-size: 0.9rem;
            margin-top: 1rem;
        }
        </style>
    """

def get_ai_analysis_css():
    """Return the CSS for the AI analysis section"""
    return """
        <style>
        .ai-analysis-container {
            margin: 20px 0;
            /* Add styles previously applied inline to the inner div */
            background-color: rgba(75, 75, 255, 0.1);
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #4B4BFF;
            font-size: 1.1em;
            line-height: 1.3;
            white-space: normal;
        }
        .ai-analysis-header {
            color: #4B4BFF;
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        .ai-analysis-text {
            color: #FFF;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        /* Removed .ai-analysis-content as it's no longer used */
        </style>
    """

def get_penalties_section_css():
    """Return the CSS for the penalties section block, header, and text."""
    return """
    <style>
    .penalties-container {
        background: #23232b;
        border-radius: 8px;
        padding: 24px 32px 18px 32px;
        margin: 32px 0 24px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #FF4B4B;
    }
    .penalties-header {
        color: #FF4B4B;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: 0.01em;
    }
    .penalties-text {
        color: #fafafa;
        font-size: 1.1rem;
        margin-bottom: 0;
        line-height: 1.5;
    }
    </style>
    """

def get_countdown_section_css():
    """Return the CSS for countdown section"""
    return """
        <style>
        .countdown-container {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .countdown-header {
            color: #FF4B4B;
            margin-bottom: 15px;
            font-size: 1.4em;
        }
        .countdown-text {
            color: #FFF;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        </style>
    """

def get_logo_css():
    """Return the CSS for logo styling"""
    return """
        <style>
        .logo-image {
            width: 230px;
            display: block;
            margin: 0 auto;
            padding: 0.5rem;
        }
        
        /* Center logo in sidebar */
        section[data-testid="stSidebarContent"] img {
            display: block;
            margin: 0 auto;
            width: 230px;
            padding: 0.5rem;
        }
        
        /* Ensure logo container is centered */
        section[data-testid="stSidebarContent"] div:has(> img) {
            text-align: center;
            width: 100%;
            padding: 0.5rem 0;
        }
        </style>
    """

def get_expiry_text_css():
    """Return the CSS for expiry text"""
    return """
        <style>
        .expiry-text {
            font-weight: bold;
        }
        </style>
    """

def get_spacing_css():
    """Return the CSS for spacing adjustments"""
    return """
        <style>
        .negative-margin-top {
            margin-top: -40px;
        }
        </style>
    """

def get_data_discovery_css():
    """Return the CSS for the data discovery page"""
    return """
        <style>
        /* Page container styling */
        div[data-testid="stVerticalBlock"] > div > div:has(div.stHeader) {
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        /* Blended navigation button styling */
        div[data-testid="stSidebarNav"] div[data-testid="stButton"] > button {
            width: 100%;
            padding: 0.5rem;
            margin: 0.25rem 0;
            background-color: transparent !important;
            color: #fafafa;
            border: none !important;
            border-radius: 0.3rem;
            text-align: left;
            transition: color 0.2s;
        }
        
        /* Hover effect for blended navigation buttons */
        div[data-testid="stSidebarNav"] div[data-testid="stButton"] > button:hover:not(:disabled) {
            background-color: transparent !important;
            color: #6fa8dc !important;
            border: none !important;
        }
        
        /* File uploader styling - text color */
        [data-testid="stFileUploader"] p {
            font-size: 14px !important;
            color: #aaa !important;
        }
        
        /* ONLY target the browse button within file uploader */
        [data-testid="stFileUploader"] button[kind="secondary"] {
            padding: 4px 12px !important;
            font-size: 14px !important;
            height: auto !important;
            min-height: 32px !important;
            line-height: 1.2 !important;
            background-color: #4B4BFF !important;
            border-radius: 4px !important;
            margin: 5px !important;
            width: auto !important;
        }
        
        /* Improve the dropzone size - very specific selector */
        [data-testid="stFileUploader"] section {
            max-width: 500px !important;
            padding: 15px !important;
            border: 1px dashed #555 !important;
            border-radius: 5px !important;
        }
        
        /* Make the entire file uploader more compact - strict selector */
        [data-testid="stFileUploader"] {
            max-width: 500px !important;
        }
        
        /* Analysis results styling */
        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 10px;
        }
        
        /* Make high-risk items stand out */
        .high-risk { 
            color: #FF4B4B !important;
            font-weight: bold;
        }
        </style>
    """

def get_magic_quadrant_css():
    """Return the CSS for the magic quadrant section"""
    return """
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
    """

def get_ai_report_css():
    """Return the CSS for the AI report section"""
    return """
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
    """

def get_penalties_note_css():
    """Return the CSS for the penalties note section"""
    return """
        <style>
        .penalties-note {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px 20px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.9em;
            color: #aaa;
            border-left: 3px solid #4B4BFF;
        }
        </style>
    """

def get_download_button_css():
    """Return the CSS for download button styling"""
    return """
        <style>
        /* Download button specific styles */
        div[data-testid="stDownloadButton"] button {
            background-color: #ffd966 !important; /* Magic Quadrant yellow */
            color: #23232b !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.4rem 1rem !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            margin: 1rem 0 !important;
            min-width: 120px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 8px !important;
        }
        
        div[data-testid="stDownloadButton"] button:hover {
            background-color: #e6c200 !important; /* Slightly darker yellow for hover */
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 8px rgba(0,0,0,0.15) !important;
        }
        
        div[data-testid="stDownloadButton"] button:active {
            background-color: #bfa000 !important;
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        div[data-testid="stDownloadButton"] button:disabled {
            background-color: #cccccc !important;
            color: #666666 !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }
        
        /* Icon styling */
        div[data-testid="stDownloadButton"] button::before {
            content: "📥";
            font-size: 1.2em;
            margin-right: 8px;
        }
        </style>
    """
