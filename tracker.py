# tracker.py (Inside your central repository)
import streamlit as st
import datetime
import hashlib
import json
import urllib.request  # Pure Python standard library (Zero installer crashes)

def log_viewer_activity(app_name: str):
    """Safely logs unique session fingerprints to a Google Sheet via a lightweight Web App."""
    current_host = st.context.headers.get("host", "")
    
    # SECURITY LOCK: Change "srinivasta" to match your exact Streamlit cloud profile workspace name
    if "srinivasta" not in current_host.lower() and "localhost" not in current_host:
        return 

    if "logged_visit" not in st.session_state:
        try:
            # 1. Gather browser tracking strings safely
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            user_ip = st.context.ip_address or "Local"
            
            # Anonymize user data into a clean 16-character fingerprint hash
            fingerprint_payload = f"{user_agent}-{user_ip}"
            user_fingerprint = hashlib.sha256(fingerprint_payload.encode()).hexdigest()[:16]
            
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"

            # Prepare the log row data package
            payload = {
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }

            # 2. Get the target macro URL hidden inside your secrets dashboard
            google_script_url = st.secrets["google_analytics_url"]
            
            # 3. Stream data package over the network via POST
            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                google_script_url, 
                data=data_bytes, 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # Send data and close the connection immediately (Maximum timeout of 3 seconds)
            with urllib.request.urlopen(req, timeout=3) as response:
                pass
            
            st.session_state.logged_visit = True
        except Exception:
            pass # Silent handling guarantees your apps never crash if Google responds slowly
