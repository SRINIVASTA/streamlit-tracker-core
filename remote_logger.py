# remote_logger.py (TEST MODE)
import datetime
import hashlib
import json
import urllib.request
import urllib.error
import streamlit as st

def run_portfolio_tracker():
    """
    Central logging module executed natively by your 60+ apps.
    Sends raw analytics payload metrics straight to your Google Sheet.
    """
    # 🔄 RUN-ONCE DEBOUNCE BLOCK
    if "analytics_logged" not in st.session_state:
        # 🧪 TEMP LOG FOR DEBUGGING
        st.write("🔍 Telemetry Loop Started...")
        
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            user_ip = getattr(st.context, "ip_address", "Local") or "Local"
            
            user_fingerprint = hashlib.sha256(f"{user_agent}-{user_ip}".encode()).hexdigest()[:16]
            
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"
            
            # 🌐 Web App Name Check
            current_host = st.context.headers.get("host", "").lower()
            if "localhost" in current_host or not current_host:
                app_name = "Local_Test_Environment"
            else:
                app_name = current_host.split(".")[0]

            payload = {
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }
            
            st.write(f"📦 Payload assembled successfully: `{payload}`")

            # 🚀 Hardcoded macro script route link 
            tracking_endpoint = "https://google.com"

            req = urllib.request.Request(
                tracking_endpoint, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            st.write("📤 Attempting network dispatch to Google Sheet...")
            
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = response.read().decode('utf-8')
                    st.success(f"✅ Server Response: {res_data}")
            except urllib.error.HTTPError as e:
                # Catch if Google redirects successfully
                if e.code in [302, 303]:
                    st.success("✅ Log successful! (Bypassed Google 302 Redirect)")
                else:
                    st.error(f"❌ Network HTTPError Code: {e.code}")
            except urllib.error.URLError as e:
                st.error(f"❌ Network URLError Reason: {e.reason}")
            
            st.session_state.analytics_logged = True
            
        except Exception as main_error:
            # 🚨 CRITICAL: Print the exact python error causing the script to quit
            st.error(f"💥 Telemetry Core Crashed! Error Message: {str(main_error)}")

# Run it
run_portfolio_tracker()
