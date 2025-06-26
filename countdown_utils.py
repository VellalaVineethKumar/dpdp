from datetime import datetime
import streamlit as st
import time
import functools

@functools.lru_cache(maxsize=1)
def get_questionnaire_cached():
    """Cache the questionnaire to prevent repeated loading"""
    if 'current_questionnaire' in st.session_state:
        return st.session_state.current_questionnaire
    return None

def create_countdown_timer():
    """Create a countdown timer that updates automatically"""
    # Initialize timer container in session state if not exists
    if 'timer_container' not in st.session_state:
        st.session_state.timer_container = st.empty()

    # Get cached questionnaire to prevent reloading
    get_questionnaire_cached()
    
    # Calculate time remaining
    deadline = datetime(2025, 12, 31, 23, 59, 59)
    now = datetime.now()
    diff = deadline - now

    days = diff.days
    hours = int((diff.seconds / 3600) % 24)
    minutes = int((diff.seconds / 60) % 60)
    seconds = int(diff.seconds % 60)

    # Auto-refresh with minimal logging
    if 'suppress_logs' not in st.session_state:
        st.session_state.suppress_logs = True
    with st.session_state.timer_container:
        # Reuse existing container to prevent recreation
        st.markdown(f"""
            <style>
            .countdown-timer {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
            }}
            .countdown-item {{
                background: #1E1E1E;
                padding: 20px;
                border-radius: 8px;
                min-width: 120px;
                text-align: center;
                border: 1px solid #444;
            }}
            .countdown-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #FF4B4B;
                margin-bottom: 5px;
                font-family: monospace;
            }}
            .countdown-label {{
                color: #CCC;
                font-size: 0.9em;
                text-transform: uppercase;
            }}
            </style>
            <div class="countdown-timer">
                <div class="countdown-item">
                    <div class="countdown-value">{days:02d}</div>
                    <div class="countdown-label">Days</div>
                </div>
                <div class="countdown-item">
                    <div class="countdown-value">{hours:02d}</div>
                    <div class="countdown-label">Hours</div>
                </div>
                <div class="countdown-item">
                    <div class="countdown-value">{minutes:02d}</div>
                    <div class="countdown-label">Minutes</div>
                </div>
                <div class="countdown-item">
                    <div class="countdown-value">{seconds:02d}</div>
                    <div class="countdown-label">Seconds</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
