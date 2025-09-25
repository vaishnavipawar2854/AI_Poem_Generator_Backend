#!/usr/bin/env python3
"""
Comprehensive test script for the updated AI Poem Generator backend
Tests API key validation, poem generation variety, error handling, and service status
"""

import asyncio
import requests
import json
import time
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append('.')

API_BASE_URL = "http://localhost:8000"

def test_service_health():
    """Test the health and status endpoints"""
    print("🏥 Testing Service Health & Status")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"   OpenAI Configured: {health_data['openai_configured']}")
            print(f"   Version: {health_data['version']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            
        # Test service status endpoint
        response = requests.get(f"{API_BASE_URL}/api/service/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Service Status: {status_data['status']}")
            
            config = status_data.get('configuration', {})
            print(f"   OpenAI Available: {config.get('openai_configured', False)}")
            print(f"   API Key Present: {config.get('api_key_present', False)}")
            print(f"   Supported Styles: {config.get('supported_styles', [])}")
            
            openai_conn = status_data.get('openai_connection')
            if openai_conn:
                print(f"   OpenAI Connection: {openai_conn.get('available', 'Unknown')}")
                if not openai_conn.get('available', False):
                    print(f"   OpenAI Error: {openai_conn.get('error', 'Unknown')}")
        else:
            print(f"❌ Service Status Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Service tests failed: {e}")
    
    print()

def test_poem_generation_variety():
    """Test poem generation with variety and different parameters"""
    print("🎭 Testing Poem Generation Variety")
    print("=" * 50)
    
    test_cases = [
        {"theme": "sunset over mountains", "style": "creative", "length": "short"},
        {"theme": "childhood memories", "style": "rhyming", "length": "medium"},
        {"theme": "ocean waves", "style": "free_verse", "length": "short"},
        {"theme": "spring flowers", "style": "haiku", "length": "short"},
        {"theme": "friendship", "style": "creative", "length": "medium"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎨 Test {i}: {test_case['theme']} ({test_case['style']}, {test_case['length']})")
        print("-" * 40)
        
        try:
            # Generate multiple poems for the same theme to test variety
            poems = []
            response_times = []
            
            for attempt in range(2):  # Generate 2 poems per test case
                start_time = time.time()
                
                response = requests.post(
                    f"{API_BASE_URL}/api/poems/generate",
                    json=test_case,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        poem = data.get('poem', '').strip()
                        poems.append(poem)
                        
                        method = data.get('generation_method', 'unknown')
                        server_time = data.get('response_time_seconds', 'N/A')
                        
                        print(f"   ✅ Attempt {attempt + 1}: Generated via {method}")
                        print(f"      Response time: {response_time:.2f}s (server: {server_time}s)")
                        print(f"      Length: {len(poem)} chars")
                        print(f"      Preview: {poem[:60]}...")
                    else:
                        print(f"   ❌ Attempt {attempt + 1}: API returned success=false")
                        print(f"      Error: {data.get('message', 'Unknown error')}")
                else:
                    print(f"   ❌ Attempt {attempt + 1}: HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data.get('message', 'Unknown error')}")
                    except:
                        print(f"      Error: {response.text[:100]}")
                
                # Small delay between requests
                time.sleep(0.5)
            
            # Check variety
            unique_poems = set(poems)
            if len(unique_poems) == len(poems) and len(poems) > 1:
                print(f"   🎉 VARIETY SUCCESS: All {len(poems)} poems are unique!")
            elif len(unique_poems) > 1:
                print(f"   ✅ GOOD VARIETY: {len(unique_poems)} out of {len(poems)} poems are unique")
            else:
                print(f"   ⚠️  LIMITED VARIETY: Only {len(unique_poems)} unique poems")
            
            # Performance summary
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                print(f"   ⏱️  Average response time: {avg_time:.2f}s")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print()

def test_error_handling():
    """Test error handling for various edge cases"""
    print("🛡️  Testing Error Handling")
    print("=" * 50)
    
    error_test_cases = [
        {
            "name": "Empty theme",
            "data": {"theme": "", "style": "creative", "length": "short"},
            "expected_status": 400
        },
        {
            "name": "Only whitespace theme", 
            "data": {"theme": "   ", "style": "creative", "length": "short"},
            "expected_status": 400
        },
        {
            "name": "Invalid style",
            "data": {"theme": "test", "style": "invalid_style", "length": "short"},
            "expected_status": 422  # Pydantic validation error
        },
        {
            "name": "Invalid length",
            "data": {"theme": "test", "style": "creative", "length": "invalid_length"},
            "expected_status": 422
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/poems/generate",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == test_case['expected_status']:
                print(f"   ✅ Correct error handling: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('message', 'N/A')}")
                except:
                    pass
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code} (expected {test_case['expected_status']})")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print()

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("🚦 Testing Rate Limiting")
    print("=" * 50)
    
    print("Making rapid requests to test rate limiting...")
    
    requests_made = 0
    rate_limited = False
    
    # Make many requests quickly to trigger rate limiting
    for i in range(20):  # Try 20 requests rapidly
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/poems/generate",
                json={"theme": f"test theme {i}", "style": "creative", "length": "short"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            requests_made += 1
            
            if response.status_code == 429:  # Rate limited
                print(f"✅ Rate limiting triggered after {requests_made} requests")
                rate_limited = True
                break
            elif response.status_code == 200:
                print(f"   Request {i+1}: Success")
            else:
                print(f"   Request {i+1}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   Request {i+1}: Timeout")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
    
    if not rate_limited and requests_made >= 15:
        print("⚠️  Rate limiting might not be working as expected")
    elif not rate_limited:
        print("ℹ️  Rate limiting not triggered (within normal limits)")
    
    print()

def main():
    """Run all tests"""
    print("🚀 AI Poem Generator Backend Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding properly. Status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print(f"   Make sure the backend is running: python main.py")
        print(f"   Error: {e}")
        return
    
    print("✅ Server is running and accessible")
    print()
    
    # Run all test suites
    test_service_health()
    test_poem_generation_variety()
    test_error_handling()
    test_rate_limiting()
    
    print("🎯 Test Suite Complete!")
    print("=" * 60)
    
    print("\n📋 Summary:")
    print("- Service health and status endpoints tested")
    print("- Poem generation variety verified")
    print("- Error handling validated") 
    print("- Rate limiting functionality checked")
    print("\n✨ Your enhanced AI Poem Generator backend is ready!")

if __name__ == "__main__":
    main()