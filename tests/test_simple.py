import requests
import json

def test_simple_variety():
    """Quick test for poem variety"""
    print("🧪 Testing Poem Variety (Simple Test)")
    print("=" * 40)
    
    # Test same parameters multiple times
    payload = {"theme": "nature", "style": "creative", "length": "short"}
    
    print(f"Testing theme: {payload['theme']}")
    print(f"Style: {payload['style']}, Length: {payload['length']}")
    print("-" * 40)
    
    for i in range(3):
        try:
            response = requests.post(
                "http://localhost:8000/api/poems/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    poem = data.get('poem', '').strip()
                    print(f"\n✅ Poem {i+1}:")
                    print(f"{poem}")
                    print(f"Length: {len(poem)} characters")
                else:
                    print(f"❌ Poem {i+1}: API returned success=false")
            else:
                print(f"❌ Poem {i+1}: HTTP {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Poem {i+1}: Error - {e}")
    
    print("\n🎯 If poems are different, variety system is working!")

if __name__ == "__main__":
    test_simple_variety()