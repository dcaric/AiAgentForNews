"""
python3 smart_spider.py https://edition.cnn.com/business
python3 smart_spider.py https://www.bbc.com/business https://www.cnbc.com/world/


"""

import sys
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# Keywords remain hardcoded here for simplicity, but you could also 
# make them arguments if you wanted.
KEYWORDS = ["apple", "nvidia", "google", "tesla", "tsla", "musk", "ai", "meta"]

# --- 1. THE FETCHER (Playwright) ---
def get_dynamic_content(url):
    """
    Launches a real (invisible) browser to load the page and run JavaScript.
    """
    print(f"   🔄 Launching Browser...")
    with sync_playwright() as p:
        # Launch Chrome (headless=True means invisible)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Go to URL
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll down to trigger lazy-loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(2) 
            
            # Get HTML
            content = page.content()
        except Exception as e:
            print(f"      ⚠️ Browser Error: {e}")
            content = ""
        finally:
            browser.close()
            
    return content

# --- 2. THE PARSER (BeautifulSoup) ---
def scan_site(url):
    # Auto-detect site name from URL (e.g., "edition.cnn.com")
    site_name = urlparse(url).netloc.replace("www.", "")
    print(f"\n📡 Scanning {site_name}...")
    
    html_content = get_dynamic_content(url)
    
    if not html_content:
        print("      ❌ Failed to retrieve content.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find ALL links
    links = soup.find_all('a', href=True)
    found_articles = []

    print(f"   🔎 Analyzing {len(links)} links...")

    for link in links:
        href = link['href']
        text = link.get_text(" ", strip=True).lower() 
        title_attr = link.get("title", "").lower()
        full_text = f"{text} {title_attr}"
        
        # Normalize URL
        full_url = urljoin(url, href)
        
        # Check Keywords
        for key in KEYWORDS:
            if key in full_text or key in href.lower():
                if "icon" in href or len(text) < 5: 
                    continue
                
                found_articles.append({
                    "headline": text[:80].title(),
                    "url": full_url,
                    "match": key.upper()
                })
                break 

    # Remove duplicates
    unique_articles = {v['url']: v for v in found_articles}.values()
    
    if not unique_articles:
        print("      🚫 No relevant articles found.")
    
    for article in unique_articles:
        print(f"   ✅ [{article['match']}] {article['headline']}")
        print(f"      🔗 {article['url']}")

# --- EXECUTE ---
if __name__ == "__main__":
    # Check if user provided URLs
    if len(sys.argv) < 2:
        print("\n❌ Error: No URLs provided.")
        print("Usage:   python3 smart_spider.py <URL1> <URL2> ...")
        print("Example: python3 smart_spider.py https://bbc.com/business https://cnbc.com")
        sys.exit(1)
    
    # Loop through all URLs provided in command line
    for target_url in sys.argv[1:]:
        scan_site(target_url)