# Shared Configuration for News Agent and Trading Simulation

# --- TRADING STRATEGY RULES ---
"""
DETAILED STRATEGY EXPLANATION:

1. GLOBAL & NEWS (Safety First):
   - If Global Context or Company News is NEGATIVE -> AVOID/SELL.
   - Logic: Don't buy "falling knives" (crashing stocks with bad news).

2. TAKE PROFIT (Lock in Gains):
   - TRIGGER: Price > 5% above Avg Entry Price.
   - Logic: Secures profit after a significant rise. Prevents selling too early on small bounces.
     Example: Bought at $100. Price hits $105.50 -> SELL.

3. STOP LOSS (Protection):
   - TRIGGER: Price < 5% below Avg Entry Price.
   - Logic: Limits max loss per position. "Stop the bleeding".
     Example: Bought at $100. Price hits $94.50 -> SELL.

4. DIP BUY (Value Investing):
   - TRIGGER: Price down > 2% (24h) AND News is NOT Negative.
   - Logic: Buys good stocks that are temporarily oversold.

5. MOMENTUM BUY (Trend Following):
   - TRIGGER: Price up > 3% (24h).
   - Logic: Catches stocks breaking out or rallying.

6. HOLD:
   - Default action if no other rule triggers.
"""
TRADING_RULES = [
    "1. ANALYZE GLOBAL IMPACT & NEWS: Are there major headwinds? If NEWS is NEGATIVE, SELL/AVOID.",
    "2. TAKE PROFIT: If we own the stock AND price is > 5% above Avg Entry, SELL (Lock in gains).",
    "3. STOP LOSS: If we own the stock AND price is < 5% below Avg Entry, SELL (Stop the bleeding).",
    "4. DIP BUY: If we DO NOT own it: Price down > 2% (Overreaction) AND News is NOT Negative -> BUY.",
    "5. MOMENTUM: If we DO NOT own it: Price up > 3% (FOMO) -> BUY.",
    "6. HOLD: If none of the above trigger, HOLD."
]

# List of stocks to track and trade
MARKET_UNIVERSE = [
    # Tech / Growth 
    "AAPL", "TSLA", "NVDA", "AMD", "MSFT", 
    "AMZN", "GOOGL", "META", "INTC", "PLTR",
    
    # Defensive / Value / Dow Jones 
    "JPM", "V", "MA", "BAC",
    "JNJ", "PFE", "MRK", "UNH",
    "WMT", "PG", "KO", "PEP", "HD", "MCD", 
    "XOM", "CVX", "ORCL"
]

"""
Tech / Growth (10):

Apple (AAPL), Tesla (TSLA), Nvidia (NVDA), AMD, Microsoft (MSFT)
Amazon (AMZN), Google (GOOGL), Meta (META), Intel (INTC), Palantir (PLTR)
Value / Defensive / Dow (10):

Finance: JPMorgan (JPM)
Healthcare: Johnson & Johnson (JNJ)
Retail/Consumer: Walmart (WMT), Home Depot (HD), McDonald's (MCD), Procter & Gamble (PG), Coca-Cola (KO)
Energy: Exxon Mobil (XOM), Chevron (CVX)
Tech/software (Value): Oracle (ORCL)




1. Finance 🏦
    JPM (JPMorgan Chase) - Largest US bank.
    V (Visa) - Payments network.
    MA (Mastercard) - Payments network.
    BAC (Bank of America) - Major US bank.
2. Healthcare ⚕️
    JNJ (Johnson & Johnson) - Pharmaceuticals and medical devices.
    PFE (Pfizer) - Pharmaceuticals.
    MRK (Merck) - Pharmaceuticals.
    UNH (UnitedHealth) - Managed healthcare.
3. Retail & Consumer Goods 🛒
    WMT (Walmart) - Retail giant.
    HD (Home Depot) - Home improvement retail.
    MCD (McDonald's) - Fast food restaurants.
    PG (Procter & Gamble) - Household consumer goods.
    KO (Coca-Cola) - Beverages.
    PEP (PepsiCo) - Beverages & Snacks.
4. Energy 🛢️
    XOM (Exxon Mobil) - Oil & Gas giant.
    CVX (Chevron) - Oil & Gas giant.
5. Tech & Growth 💻
    AAPL (Apple) - Consumer electronics.
    TSLA (Tesla) - EV & Robotics.
    NVDA (Nvidia) - AI Chips.
    AMD (AMD) - Semiconductors.
    MSFT (Microsoft) - Software & Cloud.
    AMZN (Amazon) - E-commerce & Cloud.
    GOOGL (Google) - Search & AI.
    META (Meta) - Social Media & VR.
    INTC (Intel) - Semiconductors.
    PLTR (Palantir) - AI Data Analytics.

    

"""
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
