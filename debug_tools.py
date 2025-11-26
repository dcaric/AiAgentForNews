import google.generativeai as genai
import os

print(f"SDK Version: {genai.__version__}")

try:
    from google.generativeai import types
    print("Types available:", dir(types))
    
    # Check if GoogleSearch exists in types
    if hasattr(types, 'GoogleSearch'):
        print("✅ types.GoogleSearch exists")
    else:
        print("❌ types.GoogleSearch does NOT exist")
        
    # Check Tool fields
    try:
        t = types.Tool(google_search=types.GoogleSearch())
        print("✅ Successfully created Tool with google_search")
    except Exception as e:
        print(f"❌ Failed to create Tool with google_search: {e}")

except Exception as e:
    print(f"Error inspecting types: {e}")

# Try to initialize model with dict
try:
    print("\nAttempting to initialize model with dict [{'google_search': {}}]...")
    model = genai.GenerativeModel('gemini-1.5-flash', tools=[{'google_search': {}}])
    print("✅ Model initialized successfully")
except Exception as e:
    print(f"❌ Model initialization failed: {e}")
