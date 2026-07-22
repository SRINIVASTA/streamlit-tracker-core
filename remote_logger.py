# remote_logger.py (Central logging engine)
import datetime
import hashlib
import json
import os
import urllib.request
import streamlit as st

def run_portfolio_tracker():
    """
    Central logging module executed natively by your 60+ apps.
    Sends raw analytics payload metrics straight to your Google Sheet.
    """
    # 🛡️ FIXED SECURITY OVERRIDE LOCK
    # Streamlit Cloud apps run on share.streamlit.io, or localhost during testing
    current_host = st.context.headers.get("host", "").lower()
    if "streamlit" not in current_host and "localhost" not in current_host:
        return 

    # 🔄 RUN-ONCE DEBOUNCE BLOCK
    # Ensures only one logging line entry is written per tab session
    if "analytics_logged" not in st.session_state:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            user_ip = st.context.ip_address or "Local"
            
            # Anonymizes user profiles into a secure 16-character tracking fingerprint
            user_fingerprint = hashlib.sha256(f"{user_agent}-{user_ip}".encode()).hexdigest()[:16]
            
            # Extracts unique browser window tab session tokens
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"
            
            # 📊 FIXED APP NAME DETECTION
            # Automatically grabs the active repository directory name (e.g., 'streamlit-portfolio-analytics')
            app_name = os.path.basename(os.getcwd()) if os.path.basename(os.getcwd()) else "Unknown_App"

            payload = {
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }

            # 🚀 ZERO-DEPENDENCY NETWORK DISPATCHER
            # Pings the private script URL saved under your global workspace secrets panel
            req = urllib.request.Request(
                st.secrets["google_analytics_url"], 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # Dispatches tracking attributes and closes connection under 3 seconds
            with urllib.request.urlopen(req, timeout=3) as response:
                pass
            
            # Locks state verification flag
            st.session_state.analytics_logged = True
        except Exception:
            pass # Silent handling guarantees your apps never throw runtime errors

# Execute analytics loop automatically on boot
run_portfolio_tracker()
