#!/usr/bin/env python3
"""
Comprehensive Deployment Test Suite
Tests both local DXF conversion and remote Streamlit deployments.
"""

import sys
import subprocess
from pathlib import Path
from check_streamlit import check_streamlit_deployment
from project_status import main as check_project_status

def test_local_conversion():
    """Test local DXF to PDF conversion functionality."""
    print("🔧 Testing Local DXF Conversion:")
    print("-" * 40)
    
    try:
        # Run project status check
        result = subprocess.run([sys.executable, 'project_status.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Local conversion system is healthy")
            return True
        else:
            print("❌ Local conversion system has issues")
            print(f"   Details: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing local conversion: {e}")
        return False

def test_streamlit_deployments():
    """Test multiple Streamlit deployment URLs."""
    print("\n🌐 Testing Streamlit Deployments:")
    print("-" * 40)
    
    # Common Streamlit deployment URLs to test
    test_urls = [
        "https://pdf-structure-mahipal-katara.streamlit.app",
        "https://dxf-to-pdf-converter.streamlit.app",
        "https://mahipal-katara-pdf.streamlit.app",
    ]
    
    results = []
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = check_streamlit_deployment(url, timeout=15, max_retries=2)
        results.append((url, result))
        
        if result["status"] == "SUCCESS":
            print(f"   ✅ ONLINE - Response: {result['response_time_sec']}s")
        else:
            print(f"   ❌ OFFLINE - {result.get('error', 'Unknown error')}")
    
    successful = sum(1 for _, result in results if result["status"] == "SUCCESS")
    print(f"\n📊 Deployment Summary: {successful}/{len(test_urls)} apps online")
    
    return successful > 0

def test_github_repository():
    """Test GitHub repository accessibility."""
    print("\n📂 Testing GitHub Repository:")
    print("-" * 40)
    
    try:
        # Check if we can access the remote
        result = subprocess.run(['git', 'ls-remote', 'origin'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ GitHub repository is accessible")
            
            # Check if we're up to date
            status_result = subprocess.run(['git', 'status', '-uno'], 
                                         capture_output=True, text=True, timeout=10)
            
            if "up to date" in status_result.stdout.lower():
                print("✅ Local repository is up to date")
            else:
                print("⚠️  Local repository may need sync")
            
            return True
        else:
            print("❌ Cannot access GitHub repository")
            return False
            
    except Exception as e:
        print(f"❌ Error checking GitHub: {e}")
        return False

def generate_deployment_report():
    """Generate a comprehensive deployment report."""
    print("\n" + "="*60)
    print("🚀 COMPREHENSIVE DEPLOYMENT TEST REPORT")
    print("="*60)
    
    # Test local system
    local_ok = test_local_conversion()
    
    # Test Streamlit deployments
    streamlit_ok = test_streamlit_deployments()
    
    # Test GitHub repository
    github_ok = test_github_repository()
    
    # Generate summary
    print("\n" + "="*60)
    print("📋 FINAL DEPLOYMENT STATUS")
    print("="*60)
    
    print(f"🔧 Local System:     {'✅ HEALTHY' if local_ok else '❌ ISSUES'}")
    print(f"🌐 Streamlit Apps:   {'✅ ONLINE' if streamlit_ok else '❌ OFFLINE'}")
    print(f"📂 GitHub Repo:     {'✅ ACCESSIBLE' if github_ok else '❌ ISSUES'}")
    
    overall_status = local_ok and (streamlit_ok or github_ok)
    
    print("\n" + "-"*60)
    if overall_status:
        print("🎉 DEPLOYMENT STATUS: OPERATIONAL ✅")
        print("Your DXF to PDF system is ready for use!")
    else:
        print("⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION ❌")
        print("Some components need fixing before full deployment.")
    
    print("="*60)
    
    return overall_status

def main():
    """Main deployment test function."""
    if len(sys.argv) > 1:
        # Test specific Streamlit URL
        url = sys.argv[1]
        print(f"Testing specific URL: {url}")
        result = check_streamlit_deployment(url)
        
        print("\n" + "="*50)
        print("STREAMLIT DEPLOYMENT HEALTH CHECK")
        print("="*50)
        print(f"Target URL : {url}")
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
        
        return result["status"] == "SUCCESS"
    else:
        # Run comprehensive test
        return generate_deployment_report()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)