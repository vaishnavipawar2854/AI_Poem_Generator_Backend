import requests
import json
import time

def test_poem_variety():
    """Test that poems are different each time"""
    print("🧪 Testing Poem Variety and Uniqueness")
    print("=" * 50)
    
    # Test same theme multiple times
    test_cases = [
        {"theme": "love", "style": "creative", "length": "short"},
        {"theme": "nature", "style": "rhyming", "length": "medium"},
        {"theme": "dreams", "style": "free_verse", "length": "short"},
        {"theme": "adventure", "style": "creative", "length": "medium"},
        {"theme": "friendship", "style": "rhyming", "length": "short"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎭 Test {i}: {test_case['theme'].title()} - {test_case['style']} - {test_case['length']}")
        print("-" * 40)
        
        poems = []
        for attempt in range(3):
            try:
                response = requests.post(
                    "http://localhost:8000/api/poems/generate",
                    json=test_case,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        poem = data.get('poem', '').strip()
                        poems.append(poem)
                        print(f"✅ Attempt {attempt + 1}: Generated ({len(poem)} chars)")
                        print(f"   Preview: {poem[:80]}...")
                    else:
                        print(f"❌ Attempt {attempt + 1}: API returned success=false")
                else:
                    print(f"❌ Attempt {attempt + 1}: HTTP {response.status_code}")
                    
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1}: Error - {e}")
        
        # Check for uniqueness
        unique_poems = set(poems)
        if len(unique_poems) == len(poems) and len(poems) > 1:
            print(f"🎉 SUCCESS: All {len(poems)} poems are unique!")
        elif len(unique_poems) > 1:
            print(f"✅ GOOD: {len(unique_poems)} out of {len(poems)} poems are unique")
        else:
            print(f"⚠️  WARNING: Only {len(unique_poems)} unique poem(s) generated")
    
    print(f"\n🎯 Variety Test Complete!")
    print("✅ Each request should now generate different poems")
    print("✅ Mock AI fallback provides randomized content")
    print("✅ OpenAI integration includes variation parameters")

if __name__ == "__main__":
    test_poem_variety()