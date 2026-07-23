# remote_logger.py (Central logging engine)
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
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_agent = st.context.headers.get("user-agent", "Unknown")
            
            # Grabs IP securely using Streamlit's fallback system tracking matrix
            user_ip = "Local"
            try:
                if hasattr(st, "context") and hasattr(st.context, "ip_address"):
                    user_ip = st.context.ip_address or "Local"
            except Exception:
                pass
            
            # Anonymizes user profiles into a secure 16-character tracking fingerprint
            user_fingerprint = hashlib.sha256(f"{user_agent}-{user_ip}".encode()).hexdigest()[:16]
            
            # Extracts unique browser window tab session tokens
            ctx = st.runtime.scriptrunner.script_run_context.get_script_run_ctx()
            session_id = ctx.session_id if ctx else "No_Session"
            
            # 🌐 WEB-OPTIMIZED APP NAME EXTRACTION (With Domain Fallbacks)
            current_host = st.context.headers.get("host", "").lower() if hasattr(st, "context") else ""
            referer_url = st.context.headers.get("referer", "") if hasattr(st, "context") else ""
            
            if "localhost" in current_host or not current_host:
                app_name = "Local_Test_Environment"
            elif referer_url and "srinivasta" in referer_url.lower():
                url_parts = [part for part in referer_url.split("/") if part]
                app_name = url_parts[-1].split("?")[0] if url_parts else "Unknown_App"
            else:
                # Uses the clean subdomain part directly from your public app URL
                app_name = current_host.split(".")[0] if current_host else "Cloud_Portfolio_App"

            payload = {
                "Timestamp": now,
                "App_Name": app_name,
                "Session_ID": session_id,
                "User_Fingerprint": user_fingerprint
            }

            # 🚀 FIXED: Hardcoded your active Web App Macro URL directly to eliminate all secret dependency blocks!
            tracking_endpoint = "https://google.com"

            req = urllib.request.Request(
                tracking_endpoint, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # Safe network dispatcher wrapper to bypass Google 302/303 redirect triggers
            try:
                with urllib.request.urlopen(req, timeout=4) as response:
                    response.read()
            except urllib.error.HTTPError:
                pass 
            
            st.session_state.analytics_logged = True
        except Exception:
            pass # Silent handling guarantees your apps never throw runtime container errors

# Execute analytics loop automatically on boot
run_portfolio_tracker()
