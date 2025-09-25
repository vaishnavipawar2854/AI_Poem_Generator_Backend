import sys
import os
sys.path.append('python-backend')

try:
    from services.poem_service import PoemService
    print("✅ PoemService imported successfully")
    
    # Test initialization
    service = PoemService()
    print("✅ PoemService initialized successfully")
    print(f"✅ OpenAI available: {service.is_openai_available()}")
    
except Exception as e:
    print(f"❌ Error importing/initializing PoemService: {e}")
    import traceback
    traceback.print_exc()