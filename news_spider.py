import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1. Configuration
TARGETS = [
    {"name": "BBC Business", "url": "https://www.bbc.com/business"},
    {"name": "CNN Business", "url": "https://edition.cnn.com/business"}
]

# Keywords to look for in HEADLINES or URLs
KEYWORDS = ["apple", "nvidia", "google", "tesla", "tsla", "musk", "ai"]

def scan_site(site_name, start_url):
    print(f"\n📡 Scanning {site_name}...")
    try:
        # User-Agent is crucial so they don't block you immediately
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(start_url, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find ALL links
        links = soup.find_all('a', href=True)
        found_articles = []

        for link in links:
            url = link['href']
            text = link.get_text(" ", strip=True).lower() # Get the visible text
            full_url = urljoin(start_url, url)
            
            # Check if keywords are in the TEXT or the URL
            for key in KEYWORDS:
                if key in text or key in url.lower():
                    # Filter out junk (like "apple-touch-icon")
                    if "icon" in url or len(text) < 10: 
                        continue
                        
                    found_articles.append({
                        "headline": text[:60] + "...", # First 60 chars
                        "url": full_url,
                        "match": key
                    })
                    break # Found a match, move to next link

        # Remove duplicates
        unique_articles = {v['url']: v for v in found_articles}.values()
        
        for article in unique_articles:
            print(f"   ✅ Found [{article['match'].upper()}]: {article['headline']}")
            print(f"      🔗 {article['url']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

# --- EXECUTE ---
for site in TARGETS:
    scan_site(site['name'], site['url'])