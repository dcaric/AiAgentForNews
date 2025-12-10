import sys
import json
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Load API Key from Environment Variable (Best Practice) or hardcode if testing
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_KEY)
    # Use the flexible model logic (try 2.0, fallback to 1.5)
    ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
except Exception as e:
    print(f"⚠️ Warning: Gemini not configured correctly. {e}")

# --- 2. ARGUMENT PARSING (The Change) ---
if len(sys.argv) < 2:
    print("\n❌ Error: No URLs provided.")
    print("Usage:   python3 reader_agent.py <URL1> <URL2> ...")
    print("Example: python3 reader_agent.py https://cnn.com/article1 https://bbc.com/article2\n")
    sys.exit(1)

# Take all arguments after the script name as URLs
TARGET_URLS = sys.argv[1:]

# --- 3. FUNCTIONS ---

def fetch_article_text(url):
    print(f"📖 Reading: {url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Wait for content to load
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Optional: Scroll to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            
            content = page.content()
            
            # Cleaning
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            text = soup.get_text(" ", strip=True)
            return text[:15000] # Increased limit slightly for 2.0 Flash
            
        except Exception as e:
            print(f"   ❌ Error reading: {e}")
            return None
        finally:
            browser.close()

def analyze_with_ai(text):
    prompt = f"""
    You are a Financial Analyst. Read this raw text from a news article and extract the trading signal.
    
    ARTICLE TEXT:
    {text}
    
    TASK:
    1. Identify the main Company/Stock mentioned.
    2. Determine the Sentiment (POSITIVE / NEGATIVE / NEUTRAL).
    3. Summarize the key reason in 1 sentence.
    
    OUTPUT JSON ONLY:
    {{ "ticker": "NVDA", "sentiment": "POSITIVE", "summary": "Reasoning here..." }}
    """
    
    try:
        config = genai.types.GenerationConfig(response_mime_type="application/json")
        response = ai_model.generate_content(prompt, generation_config=config)
        
        # Clean potential markdown formatting
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # --- FIX: Handle List vs Dictionary ---
        if isinstance(data, list):
            if len(data) > 0:
                return data[0] # Take the first result if it returns a list
            else:
                return None # Empty list
        
        return data

    except Exception as e:
        print(f"   ❌ AI Error: {e}")
        return None

# --- 4. EXECUTE ---
print(f"\n🤖 READER AGENT STARTED ({len(TARGET_URLS)} articles)...\n")

for url in TARGET_URLS:
    raw_text = fetch_article_text(url)
    
    if raw_text:
        print("   🧠 Analyzing sentiment...")
        analysis = analyze_with_ai(raw_text)
        
        if analysis:
            print(f"\n   ✅ REPORT:")
            print(f"      Ticker: {analysis.get('ticker')}")
            print(f"      Signal: {analysis.get('sentiment')}")
            print(f"      Reason: {analysis.get('summary')}\n")
            print("-" * 50)

print("\n🏁 Done.")