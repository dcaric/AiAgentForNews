import feedparser

feeds = [
    "https://www.dalmacijanews.hr/feed",
    "https://www.dalmacijadanas.hr/feed",
    "https://dalmatinskiportal.hr/rss"
]

for url in feeds:
    print(f"Checking {url}...")
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            print(f"  ✅ Success! Found {len(feed.entries)} entries.")
            print(f"  Sample: {feed.entries[0].title}")
        else:
            print(f"  ❌ Failed (or empty). Status: {getattr(feed, 'status', 'Unknown')}")
            # Try alternative if failed
            if "dalmatinskiportal" in url:
                 alt = "https://dalmatinskiportal.hr/feed"
                 print(f"    Trying alternative: {alt}")
                 feed = feedparser.parse(alt)
                 if feed.entries:
                     print(f"    ✅ Success! Found {len(feed.entries)} entries.")
    except Exception as e:
        print(f"  ❌ Error: {e}")
