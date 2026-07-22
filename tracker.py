# tracker.py (Inside your central repository)
import streamlit as st
import datetime
import hashlib
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def log_viewer_activity(app_name: str):
    """Safely logs unique session fingerprints using native Streamlit connections."""
    current_host = st.context.headers.get("host", "")
    
    # Change to match your team workspace domain
    if "yourworkspace.streamlit.app" not in current_host and "localhost" not in current_host:
        return 

    if "logged_visit" not in st.session_state:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            user_ip = st.context.ip_address or "Local"
            
            fingerprint_payload = f"{user_agent}-{user_ip}"
            user_fingerprint = hashlib.sha256(fingerprint_payload.encode()).hexdigest()[:16]
            
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"

            # Prepare the single row of log data
            new_log = pd.DataFrame([{
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }])

            # Connect using Streamlit's native secret integration named 'gsheets'
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # Read existing data, append the new row, and write it back
            existing_data = conn.read(spreadsheet=st.secrets["gsheets"]["spreadsheet"])
            updated_data = pd.concat([existing_data, new_log], ignore_index=True)
            
            conn.update(spreadsheet=st.secrets["gsheets"]["spreadsheet"], data=updated_data)
            
            st.session_state.logged_visit = True
        except Exception:
            pass # Fails silently so your apps never crash for users
