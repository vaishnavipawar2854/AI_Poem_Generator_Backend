import requests
import json

# Test the FastAPI backend
def test_backend():
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/health")
        print("✅ Health Check:")
        print(json.dumps(health_response.json(), indent=2))
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test poem generation
    try:
        poem_data = {
            "theme": "sunset over mountains",
            "style": "creative",
            "length": "medium"
        }
        
        poem_response = requests.post(
            f"{base_url}/api/poems/generate",
            json=poem_data,
            headers={"Content-Type": "application/json"}
        )
        
        if poem_response.status_code == 200:
            result = poem_response.json()
            print("✅ Poem Generation Test:")
            print(f"Theme: {result['theme']}")
            print(f"Style: {result['style']}")
            print(f"Length: {result['length']}")
            print(f"Using OpenAI: {result.get('using_openai', 'Unknown')}")
            print("\n📝 Generated Poem:")
            print(result['poem'])
        else:
            print(f"❌ Poem generation failed: {poem_response.status_code}")
            print(poem_response.text)
            
    except Exception as e:
        print(f"❌ Poem generation test failed: {e}")

if __name__ == "__main__":
    test_backend()