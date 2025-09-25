import asyncio
import os
import sys
sys.path.append('.')

from services.poem_service import PoemService

async def test_poem_variety():
    """Test poem generation variety directly"""
    print("🧪 Direct Poem Service Variety Test")
    print("=" * 40)
    
    # Load environment variables manually
    from dotenv import load_dotenv
    load_dotenv()
    
    service = PoemService()
    print(f"OpenAI Available: {service.is_openai_available()}")
    print("-" * 40)
    
    # Test same theme multiple times
    theme = "nature"
    style = "creative"
    length = "short"
    
    print(f"Testing: {theme} - {style} - {length}")
    print("-" * 40)
    
    poems = []
    for i in range(3):
        try:
            print(f"\n📝 Generating Poem {i+1}...")
            poem = await service.generate_poem(theme, style, length)
            poems.append(poem)
            print(f"✅ Generated ({len(poem)} chars):")
            print(poem[:100] + "..." if len(poem) > 100 else poem)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Check uniqueness
    unique_poems = set(poems)
    print(f"\n🎯 Results:")
    print(f"Total poems: {len(poems)}")
    print(f"Unique poems: {len(unique_poems)}")
    
    if len(unique_poems) == len(poems) and len(poems) > 1:
        print("🎉 SUCCESS: All poems are unique!")
    elif len(unique_poems) > 1:
        print(f"✅ GOOD: {len(unique_poems)} out of {len(poems)} poems are unique")
    else:
        print("⚠️ WARNING: Poems are identical")
    
    # Test different themes
    print(f"\n🌟 Testing Different Themes:")
    themes = ["love", "adventure", "friendship", "mystery"]
    
    for theme in themes:
        try:
            poem = await service.generate_poem(theme, "creative", "short")
            print(f"✅ {theme.title()}: {poem[:60]}...")
        except Exception as e:
            print(f"❌ {theme.title()}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_poem_variety())