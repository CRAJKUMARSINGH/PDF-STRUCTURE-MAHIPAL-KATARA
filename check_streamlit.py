#!/usr/bin/env python3
"""
Streamlit Deployment Health Checker
Programmatically test if a Streamlit app is deployed and functional.
"""

import requests
import sys
import time
from urllib.parse import urljoin
from typing import Optional

def check_streamlit_deployment(url: str, timeout: int = 30, max_retries: int = 3, delay: int = 5) -> dict:
    """
    Programmatically test if a Streamlit app is deployed and functional.
    
    Args:
        url (str): Base URL of the Streamlit app (e.g., 'https://myapp.streamlit.app')
        timeout (int): Request timeout in seconds
        max_retries (int): Number of retry attempts
        delay (int): Delay between retries in seconds
        
    Returns:
        dict: Status report with success, response time, and details
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Streamlit-Health-Checker/1.0"
    })
    
    # Ensure URL ends with '/' for proper joining
    base_url = url.rstrip("/") + "/"
    
    # Common Streamlit health endpoints
    health_endpoints = [
        "",  # Root often works for Streamlit (serves the app)
        "healthz",  # Common health check path
        "_stcore/health",  # Internal Streamlit core health
    ]
    
    for attempt in range(max_retries):
        for endpoint in health_endpoints:
            target_url = urljoin(base_url, endpoint)
            
            try:
                start_time = time.time()
                response = session.get(target_url, timeout=timeout, allow_redirects=True)
                response_time = time.time() - start_time
                
                # Streamlit app is up if:
                # - Status 200
                # - Content includes Streamlit markers (even on root)
                if response.status_code == 200:
                    content = response.text.lower()
                    is_streamlit = any(marker in content for marker in [
                        "streamlit", "st.", "<!-- streamlit", "data-testid"
                    ])
                    
                    if endpoint == "" and not is_streamlit:
                        continue  # Root responded but not a Streamlit app
                    
                    return {
                        "status": "SUCCESS",
                        "url": target_url,
                        "response_time_sec": round(response_time, 3),
                        "http_status": response.status_code,
                        "streamlit_detected": True,
                        "message": "Streamlit app is up and running."
                    }
                    
            except requests.exceptions.RequestException as e:
                error_type = type(e).__name__
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    return {
                        "status": "FAILED",
                        "url": target_url,
                        "error": error_type,
                        "message": f"Failed to reach Streamlit app: {str(e)}"
                    }
    
    return {
        "status": "FAILED",
        "message": "No valid Streamlit response after retries.",
        "checked_endpoints": health_endpoints
    }

# === MAIN EXECUTION ===
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_streamlit.py <streamlit_app_url>")
        print("Example: python check_streamlit.py https://myapp.streamlit.app")
        sys.exit(1)
    
    app_url = sys.argv[1]
    result = check_streamlit_deployment(app_url)
    
    # Print report
    print("\n" + "="*50)
    print("STREAMLIT DEPLOYMENT HEALTH CHECK")
    print("="*50)
    print(f"Target URL : {app_url}")
    print(f"Status     : {result['status']}")
    
    if result["status"] == "SUCCESS":
        print(f"Response   : {result['http_status']} in {result['response_time_sec']}s")
        print(f"Endpoint   : {result['url']}")
        print("✅ Streamlit app is FUNCTIONAL and responsive.")
    else:
        print(f"Error      : {result.get('error', 'Unknown')}")
        print(f"Details    : {result['message']}")
        print("❌ Streamlit app is NOT functional.")
    
    print("="*50)