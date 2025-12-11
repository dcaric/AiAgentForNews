
import os
import json
from google.cloud import storage

# Hardcoded from logs
BUCKET_NAME = "my-news-agent-data"
STATE_FILE_NAME = 'portfolio_ai_state.json'

def inspect_state():
    print(f"📡 Connecting to GCS Bucket: {BUCKET_NAME}...")
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(STATE_FILE_NAME)
        
        if blob.exists():
            print(f"   📂 Found state file. Downloading...")
            content = blob.download_as_text()
            state = json.loads(content)
            
            print("\n--- 📜 LAST 15 HISTORY ENTRIES ---")
            history = state.get("history", [])
            for entry in history[-15:]:
                print(f"   {entry}")
                
            print("\n--- 💼 CURRENT PORTFOLIO ---")
            print(json.dumps(state.get("portfolio", {}), indent=2))
            
            print("\n--- 💵 CASH ---")
            print(f"   ${state.get('cash', 0):.2f}")
            
        else:
            print("❌ State file not found in GCS.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_state()
