import feedparser

feeds = [
    "https://techcrunch.com/feed/",
    "https://9to5mac.com/feed/",
    "https://www.techradar.com/rss",
    "https://www.cnet.com/rss/news/",
    "https://www.economist.com/science-and-technology/rss.xml", # Specific section might be better
    "https://www.artificialintelligence-news.com/feed/",
    # Flipboard is tricky, usually per topic. Let's try a general one or search.
    # "https://flipboard.com/@topic/artificialintelligence.rss" # Guessing
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
