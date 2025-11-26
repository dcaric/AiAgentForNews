import requests
from bs4 import BeautifulSoup

urls = [
    "https://finance.yahoo.com",
    "https://www.cnbc.com/technology/",
    "https://www.marketwatch.com",
    "https://www.reuters.com/markets/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for url in urls:
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title"
            text_len = len(soup.get_text())
            print(f"✅ Success: {title} (Text length: {text_len})")
        else:
            print(f"❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
