import feedparser

feeds = [
    "https://www.index.hr/rss/vijesti",
    "https://www.tportal.hr/rss",
    "https://www.jutarnji.hr/rss/vijesti",
    "https://www.dalmacijanews.hr/feed"
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
    except Exception as e:
        print(f"  ❌ Error: {e}")
