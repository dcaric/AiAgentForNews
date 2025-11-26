import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://hnl.hr/klubovi/hajduk/"
print(f"Fetching {url}...")
try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print raw text to see what's visible
    text = soup.get_text(separator="\n", strip=True)
    print("--- RAW TEXT START ---")
    print(text[:2000])
    print("--- RAW TEXT END ---")
    
    # Look for "Sljedeća utakmica"
    keyword = "Sljedeća utakmica"
    if keyword in text:
        print(f"✅ Found '{keyword}' in text.")
        # Try to find the container
        elements = soup.find_all(string=lambda text: keyword in text if text else False)
        for i, element in enumerate(elements):
             print(f"\n--- Occurrence {i+1} ---")
             parent = element.parent
             grandparent = parent.parent if parent else None
             if grandparent:
                 # Print a larger context to see teams, date, time
                 print("Context:", grandparent.parent.get_text(separator=" | ", strip=True)[:500])
    else:
        print(f"❌ '{keyword}' not found.")
except Exception as e:
    print(f"Error: {e}")
