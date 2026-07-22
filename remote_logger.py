# remote_logger.py (Central logging engine)
import datetime
import hashlib
import json
import urllib.request
import streamlit as st

def run_portfolio_tracker():
    """
    Central logging module executed natively by your 60+ apps.
    Sends raw analytics payload metrics straight to your Google Sheet.
    """
    # 🛡️ SECURITY OVERRIDE LOCK
    current_host = st.context.headers.get("host", "").lower()
    if "streamlit" not in current_host and "localhost" not in current_host:
        return 

    # 🔄 RUN-ONCE DEBOUNCE BLOCK
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
            
            # 🌐 WEB-OPTIMIZED APP NAME EXTRACTION
            referer_url = st.context.headers.get("referer", "")
            if referer_url and "srinivasta" in referer_url.lower():
                # Strips out everything except the specific repository name component from the URL path
                url_parts = [part for part in referer_url.split("/") if part]
                app_name = url_parts[-1].split("?")[0] if url_parts else "Unknown_App"
            else:
                app_name = "Local_Test_Environment"

            payload = {
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }

            # 🚀 ZERO-DEPENDENCY NETWORK DISPATCHER
            req = urllib.request.Request(
                st.secrets["google_analytics_url"], 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=3) as response:
                pass
            
            st.session_state.analytics_logged = True
        except Exception:
            pass # Silent handling guarantees your apps never throw runtime errors

# Execute analytics loop automatically on boot
run_portfolio_tracker()
