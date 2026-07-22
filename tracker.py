# tracker.py (Located in your central repo)
import streamlit as st
import datetime
import hashlib
from gsheetsdb import connect # Replace with your chosen DB driver

def log_viewer_activity(app_name: str):
    """
    Centralized function to safely track views across your portfolio.
    Protects your database from copycats and filters out unauthorized domains.
    """
    # 1. ANTI-THEFT GUARD: Verify the app is running on YOUR expected workspace or localhost
    current_host = st.context.headers.get("host", "")
    
    # Change "yourworkspace" to match your Streamlit Cloud team workspace domain name
    if "yourworkspace.streamlit.app" not in current_host and "localhost" not in current_host:
        return # Silently exit to prevent copycats from writing garbage data to your DB

    # 2. RUN-ONCE PROTECTION: Prevent re-logging on page updates/button clicks
    if "logged_visit" not in st.session_state:
        try:
            # Gather contextual user footprints without violating basic privacy
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            user_ip = st.context.ip_address or "Local"
            
            # Anonymize identity into a unique, un-spoofable fingerprint hash
            fingerprint_payload = f"{user_agent}-{user_ip}"
            user_fingerprint = hashlib.sha256(fingerprint_payload.encode()).hexdigest()[:16]
            
            # Extract unique Streamlit session id
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"

            # 3. SECURELY INSERT INTO CENTRAL DB
            # Fetches 'public_sheet_url' safely hidden inside your cloud settings dashboard
            sheet_url = st.secrets["public_sheet_url"]
            conn = connect()
            
            query = f"""
                INSERT INTO "{sheet_url}" (Timestamp, App_Name, Session_ID, User_Fingerprint)
                VALUES ('{now}', '{app_name}', '{session_id}', '{user_fingerprint}')
            """
            conn.execute(query)
            
            # Lock the tracking block for this session
            st.session_state.logged_visit = True
        except Exception:
            pass # Fail silently so your main app never displays errors to visitors
