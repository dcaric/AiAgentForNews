# Shared Configuration for News Agent and Trading Simulation

# List of stocks to track and trade
MARKET_UNIVERSE = [
    # Tech / Growth (Original)
    "AAPL", "TSLA", "NVDA", "AMD", "MSFT", 
    "AMZN", "GOOGL", "META", "INTC", "PLTR",
    
    # Defensive / Value / Dow Jones (New)
    "JPM", "JNJ", "WMT", "PG", "KO", 
    "XOM", "CVX", "HD", "MCD", "ORCL"
]

# User's current share counts for portfolio calculation
# (Also acts as the list of stocks in the user's portfolio)
MY_HOLDINGS = {
    'NVDA': 20.877,
    'AAPL': 5.486,
    'GOOG': 3.042
}

# --- RSS FEEDS ---

# Tech & AI News
TECH_NEWS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://9to5mac.com/feed/",
    "https://www.techradar.com/rss",
    "https://www.cnet.com/rss/news/",
    "https://www.economist.com/science-and-technology/rss.xml",
    "https://www.artificialintelligence-news.com/feed/",
]

# World News
WORLD_NEWS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "https://finance.yahoo.com/news/rssindex",
]

# NBA News
NBA_NEWS_FEEDS = [
    "https://www.espn.com/espn/rss/nba/news",
    "https://sports.yahoo.com/nba/rss/",
    "https://www.rotowire.com/rss/news.php?sport=NBA",
]

# Croatian News
CROATIAN_NEWS_FEEDS = [
    "https://www.index.hr/rss/vijesti",
    "https://www.tportal.hr/rss",
    "https://www.jutarnji.hr/rss",
]

# Dalmatia News
DALMATIA_NEWS_FEEDS = [
    "https://www.dalmacijanews.hr/feed",
    "https://www.dalmacijadanas.hr/feed",
    "https://dalmatinskiportal.hr/rss",
]
