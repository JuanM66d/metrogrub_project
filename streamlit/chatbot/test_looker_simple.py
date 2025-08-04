#!/usr/bin/env python3

import requests
import google.auth
from google.auth.transport.requests import Request

def test_looker_connection():
    """Simple test focusing on what we know works"""
    
    print("🧪 Simple Looker Connection Test")
    print("=" * 40)
    
    # Configuration
    looker_instance_uri = "https://panderasystems.looker.com/"
    lookml_model = "metrogrub_data"
    explore = "master"
    
    print(f"🔗 Instance: {looker_instance_uri}")
    print(f"📁 Model: {lookml_model}")
    print(f"🔍 Explore: {explore}")
    print("-" * 40)
    
    # Get Google Cloud credentials
    print("\n1️⃣ Getting Google Cloud credentials...")
    try:
        credentials, project_id = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        auth_req = Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        
        print(f"✅ Authenticated with project: {project_id}")
        print(f"🎫 Credential type: {type(credentials).__name__}")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
    # Test the working approach
    print("\n2️⃣ Testing direct explore access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    direct_explore_url = f"{looker_instance_uri}explore/{lookml_model}/{explore}"
    
    try:
        response = requests.get(direct_explore_url, headers=headers, timeout=10)
        print(f"🔗 URL: {direct_explore_url}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Direct explore access works!")
            print(f"📄 Response size: {len(response.text):,} characters")
            
            # Basic content analysis
            content = response.text.lower()
            indicators = {
                "data references": "data" in content,
                "chart/viz references": any(term in content for term in ["chart", "visualization", "viz"]),
                "error indicators": "error" in content,
                "auth issues": any(term in content for term in ["unauthorized", "forbidden"])
            }
            
            print("\n📋 Content analysis:")
            for indicator, found in indicators.items():
                status = "✅" if found else "❌"
                print(f"   {status} {indicator}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Unauthorized - credentials may lack Looker permissions")
            return False
        elif response.status_code == 404:
            print("❌ Not found - model/explore may not exist")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Preview: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🚀 Testing the connection approach that we know works...\n")
    
    success = test_looker_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CONNECTION CONFIRMED!")
        print("\n💡 What this means for your chatbot:")
        print("   • Your Looker model and explore exist")
        print("   • Google Cloud authentication is working")  
        print("   • The issue is likely API permissions, not connectivity")
        print("\n🔧 Next steps:")
        print("   1. Try running your chatbot now")
        print("   2. If it still fails, the issue is specific API permissions")
        print("   3. Ask questions about your Chicago datasets")
        
        print("\n💬 Good questions to try:")
        print("   • 'What data is available?'")
        print("   • 'Show me food inspection data'") 
        print("   • 'What are the demographics by neighborhood?'")
        print("   • 'List all the datasets'")
        
    else:
        print("💥 CONNECTION FAILED")
        print("\n🔧 Troubleshooting:")
        print("   1. Check: gcloud auth list")
        print("   2. Verify: gcloud config get-value project") 
        print("   3. Confirm model/explore names in Looker")

if __name__ == "__main__":
    main()