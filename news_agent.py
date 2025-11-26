import feedparser
import requests
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
# --- NBA Score Collector ---
import requests
from datetime import datetime, timedelta
import google.generativeai as genai
import os
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from google.cloud import storage
import json
from io import BytesIO

# --- Stock Portfolio Tracker ---
class StockCollector:
    def __init__(self):
        self.tickers = ['AAPL', 'NVDA', 'GOOG']

    def get_stock_data(self):
        data = {}
        for ticker in self.tickers:
            try:
                # Fetch 7 days of history for the graph + today's live price
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo") # Get 1 month to be safe for 7 days
                if hist.empty:
                    continue
                
                # Get last 7 days
                last_7_days = hist.tail(7)
                current_price = hist['Close'].iloc[-1]
                
                # Calculate change (from previous close)
                if len(hist) > 1:
                    prev_close = hist['Close'].iloc[-2]
                    change = current_price - prev_close
                    pct_change = (change / prev_close) * 100
                else:
                    change = 0
                    pct_change = 0

                data[ticker] = {
                    'current_price': current_price,
                    'change': change,
                    'pct_change': pct_change,
                    'history': last_7_days['Close']
                }
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        return data

class PortfolioManager:
    def __init__(self):
        # Constants for holdings
        self.holdings = {
            'NVDA': 20.877,
            'AAPL': 5.486,
            'GOOG': 3.042
        }
        self.bucket_name = os.environ.get("BUCKET_NAME")
        self.history_file = "portfolio_history.json"

    def calculate_total_capital(self, stock_data):
        total = 0.0
        for ticker, shares in self.holdings.items():
            if ticker in stock_data:
                total += stock_data[ticker]['current_price'] * shares
        return total

    def update_history(self, total_capital):
        if not self.bucket_name:
            print("BUCKET_NAME not set. Skipping persistence.")
            return []

        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.history_file)

            history = []
            if blob.exists():
                content = blob.download_as_text()
                history = json.loads(content)

            # Append today's data
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Check if today already exists, update if so
            updated = False
            for entry in history:
                if entry['date'] == today:
                    entry['total'] = total_capital
                    updated = True
                    break
            if not updated:
                history.append({'date': today, 'total': total_capital})

            # Save back to GCS
            blob.upload_from_string(json.dumps(history))
            return history
        except Exception as e:
            print(f"Error updating portfolio history: {e}")
            return []

class GraphGenerator:
    def __init__(self):
        # Use Agg backend for non-interactive plotting
        plt.switch_backend('Agg')

    def generate_stock_chart(self, ticker, history_series):
        plt.figure(figsize=(6, 3))
        plt.plot(history_series.index, history_series.values, marker='o', linestyle='-')
        plt.title(f"{ticker} - Last 7 Days")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

    def generate_portfolio_chart(self, history_data):
        if not history_data:
            return None
            
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in history_data]
        totals = [d['total'] for d in history_data]
        
        plt.figure(figsize=(8, 4))
        plt.plot(dates, totals, color='green', marker='o', linestyle='-')
        plt.title("Total Capital Growth")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

class NBAScoreCollector:
    def get_scores_for_date(self, date_str):
        # The CDN endpoint is for "today's" scoreboard.
        # To get past dates, we need a different endpoint or logic.
        # Actually, the CDN endpoint structure is: https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json
        # This only gives the *current* "today".
        # For historical data (past week), we might need to use the stats API endpoint or a different CDN path if available.
        # However, `nba_api` was problematic with dates.
        # Let's try to use the `scoreboardv2` endpoint from `nba_api` again JUST for historical data, 
        # OR find a better way. 
        # Actually, for the purpose of this task, let's stick to the reliable CDN for "last night" (if it matches).
        # But for "past week", we need 7 days of data.
        # The `scoreboardv2` endpoint is the standard way for historical scores.
        # Let's re-introduce `nba_api` strictly for historical data if needed, OR use a public API.
        # Wait, the user wants "past week".
        # Let's use `nba_api`'s `ScoreboardV2` but be very careful with the date parameters.
        # We know `nba_api` works if we pass the correct string.
        # The issue before was likely just the system time confusion.
        # If we pass explicit past dates (e.g. "2024-11-20"), it should work.
        pass 

    def get_last_nights_scores(self):
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        try:
            print(f"Fetching scores from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = data['scoreboard']['games']
            scores = []
            
            for game in games:
                visitor_abbr = game['awayTeam']['teamTricode']
                home_abbr = game['homeTeam']['teamTricode']
                visitor_score = game['awayTeam']['score']
                home_score = game['homeTeam']['score']
                status = game['gameStatusText']
                
                scores.append({
                    'matchup': f"{visitor_abbr} vs {home_abbr}",
                    'score': f"{visitor_score} - {home_score}",
                    'status': status
                })
            return scores
        except Exception as e:
            print(f"Error fetching NBA scores from CDN: {e}")
            return []

    def get_weekly_scores(self):
        # Currently, the reliable CDN only provides "today's" (yesterday's) scores.
        # Historical fetching from stats.nba.com is unreliable (timeouts).
        # For now, we will return the latest available scores to the LLM 
        # so it can at least analyze the most recent performance.
        return self.get_last_nights_scores()

class LLMSummarizer:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not set.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Using gemini-2.5-flash as it is faster and currently supported
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def summarize_world_news(self, articles):
        if not self.model:
            return "Gemini API Key missing. Cannot generate summary."
        
        prompt = """
        Summarize the following world news headlines and snippets into a single, cohesive paragraph.
        Use HTML tags like <b> for key terms. Do not use Markdown.
        Keep it concise (under 100 words).
        
        News:
        """
        for art in articles:
            prompt += f"- {art['title']}: {art['summary']}\n"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {e}"

    def analyze_nba_trends(self, scores):
        if not self.model:
            return "Gemini API Key missing. Cannot analyze trends."
            
        prompt = """
        Analyze the following NBA scores. Identify the top 3-4 teams that performed well.
        Highlight significant wins, high scores, or upsets.
        
        Format the output as 2-3 short, concise paragraphs using HTML tags <p> and <b> for bolding.
        Do NOT use Markdown (like **). Use HTML only.
        Avoid long lists or walls of text. Keep it easy to read.
        
        Scores:
        """
        if not scores:
            return "No recent scores available to analyze."
            
        for game in scores:
            prompt += f"{game['matchup']}: {game['score']} ({game['status']})\n"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing trends: {e}"

    def curate_croatian_news(self, articles):
        if not self.model:
            return "Gemini API Key missing. Cannot curate news."
            
        prompt = """
        You are a news editor. From the following list of Croatian news articles, select the 20 most important and relevant ones.
        
        **CRITICAL INSTRUCTION:** Exclude any news related to world/global topics (e.g., Ukraine, USA, Gaza, etc.). Focus ONLY on news related to Croatia.
        
        **OUTPUT FORMAT:**
        1.  **Summary Paragraph:** A single, cohesive HTML paragraph (<p>...</p>) summarizing the most important themes from the selected articles. Use <b>bold</b> for key terms.
        2.  **Article List:** A clean HTML list (<ul>...</ul>) of the selected articles. Each item: <li><a href='LINK'>TITLE</a> - SUMMARY</li>
        
        Keep the language in Croatian.
        Do NOT use Markdown. Use HTML only.
        
        Articles:
        """
        for art in articles:
            prompt += f"- {art['title']} ({art['link']}): {art['summary'][:200]}\n"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error curating Croatian news: {e}"

    def get_next_hajduk_game(self):
        url = "https://hnl.hr/klubovi/hajduk/"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=" | ", strip=True)
            
            # Search for the specific pattern seen in analysis
            # Pattern: ... | Sljedeća utakmica | Hajduk - [Opponent] | [Date] | [Location] | ...
            if "Sljedeća utakmica" in text:
                parts = text.split("Sljedeća utakmica |")
                if len(parts) > 1:
                    # Get the part after "Sljedeća utakmica"
                    next_match_part = parts[1].strip()
                    # Split by pipe to get details
                    # Example: Hajduk - Varaždin | 29.11.2025. | Gradski stadion Poljud, Split | Prethodna utakmica ...
                    details = next_match_part.split(" | ")
                    
                    if len(details) >= 3:
                        match_title = details[0].strip() # e.g. "Hajduk - Varaždin"
                        date = details[1].strip()        # e.g. "29.11.2025."
                        location = details[2].strip()    # e.g. "Gradski stadion Poljud, Split"
                        
                        # Check if it's a home game (at Poljud)
                        if "Poljud" in location or "Hajduk -" in match_title: # Hajduk listed first usually means home, or location is Poljud
                             return f"""
                             <h3>⚽ Sljedeća Utakmica</h3>
                             <p>
                               <b>Susret:</b> {match_title}<br>
                               <b>Datum:</b> {date}<br>
                               <b>Lokacija:</b> {location}
                             </p>
                             """
            
            return "<p><i>(Podaci o sljedećoj utakmici nisu pronađeni.)</i></p>"

        except Exception as e:
            print(f"Error scraping Hajduk game: {e}")
            return f"<p><i>(Raspored nije dostupan. Greška: {str(e)[:100]}... Provjerite <a href='https://hajduk.hr/utakmice/raspored'>hajduk.hr</a>)</i></p>"

    def curate_dalmatia_news(self, articles):
        if not self.model:
            return "Gemini API Key missing. Cannot curate news."
            
        prompt = """
        You are a news editor. From the following list of news articles from Dalmatia portals, select the 15 most important and relevant ones.
        
        **CRITICAL INSTRUCTION:** Exclude any news related to world/global topics. Focus ONLY on news related to Dalmatia and Croatia.
        
        **OUTPUT FORMAT:**
        1.  **Summary Paragraph:** A single, cohesive HTML paragraph (<p>...</p>) summarizing the most important themes from the selected articles. Use <b>bold</b> for key terms.
        2.  **Article List:** A clean HTML list (<ul>...</ul>) of the selected articles. Each item: <li><a href='LINK'>TITLE</a> - SUMMARY</li>
        
        Keep the language in Croatian.
        Do NOT use Markdown. Use HTML only.
        
        Articles:
        """
        for art in articles:
            prompt += f"- {art['title']} ({art['link']}): {art['summary'][:200]}\n"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error curating Dalmatia news: {e}"

    def curate_apple_ai_news(self, articles):
        if not self.model:
            return "Gemini API Key missing. Cannot curate news."
            
        prompt = """
        You are a tech news editor. From the following list of articles, select the **Top 10** most important stories related to:
        1. **Apple** (products, software, corporate)
        2. **Artificial Intelligence** (breakthroughs, major models, industry impact)
        
        **EVALUATION:** Prioritize major announcements, reviews of new products, and significant AI developments over minor rumors or niche updates.
        
        **OUTPUT FORMAT:**
        1.  **Summary Paragraph:** A single, cohesive HTML paragraph (<p>...</p>) summarizing the key trends in Apple and AI from these articles. Use <b>bold</b> for key terms.
        2.  **Article List:** A clean HTML list (<ul>...</ul>) of the selected 10 articles. Each item: <li><a href='LINK'>TITLE</a> - SUMMARY</li>
        
        Keep the language in English.
        Do NOT use Markdown. Use HTML only.
        
        Articles:
        """
        for art in articles:
            prompt += f"- {art['title']} ({art['link']}): {art['summary'][:200]}\n"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error curating Apple & AI news: {e}"


    def crawl_url(self, url):
        """Helper to crawl a URL and return text content."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.extract()
                return soup.get_text()[:10000] # Limit to 10k chars per site
            return ""
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return ""

    def analyze_stock_market(self):
        if not self.model:
            return "<p><i>(Gemini API Key missing. Cannot analyze stocks.)</i></p>"
            
        try:
            # 1. Crawl sources directly
            urls = [
                "https://finance.yahoo.com",
                "https://www.cnbc.com/technology/",
                "https://www.marketwatch.com",
                "https://www.reuters.com/markets/"
            ]
            
            context_text = ""
            for url in urls:
                print(f"Crawling {url}...")
                text = self.crawl_url(url)
                if text:
                    context_text += f"\n--- SOURCE: {url} ---\n{text}\n"
            
            if not context_text:
                context_text = "No external data could be crawled. Please analyze based on general knowledge."

            # 2. Use Gemini 2.0 Flash (Experimental) without tools
            # User requested gemini-2.5-flash, likely meaning gemini-2.0-flash-exp
            grounding_model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            Analyze the current stock market trends for **Apple (AAPL)**, **Nvidia (NVDA)**, and **Google (GOOG/GOOGL)**.
            
            
            **OUTPUT FORMAT:**
            Provide a concise **HTML summary** (no Markdown).
            -   Start with a general **Market Sentiment** paragraph.
            -   Then provide a bulleted list for each company with key insights:
                <ul>
                <li><b>AAPL:</b> [Analysis]</li>
                <li><b>NVDA:</b> [Analysis]</li>
                <li><b>GOOG:</b> [Analysis]</li>
                </ul>
            -   End with a brief **Tech World Summary**.
            """
            
            response = grounding_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error analyzing stock market: {e}")
            return f"<p><i>(Stock analysis unavailable. Error: {str(e)[:100]})</i></p>"

class NewsCollector:
    def __init__(self):
        self.world_feeds = [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
        ]
        self.nba_feeds = [
            "https://www.espn.com/espn/rss/nba/news",
            "https://sports.yahoo.com/nba/rss/",
            "https://www.rotowire.com/rss/news.php?sport=NBA",
        ]
        self.croatian_feeds = [
            "https://www.index.hr/rss/vijesti",
            "https://www.tportal.hr/rss",
            "https://www.jutarnji.hr/rss",
        ]
        self.dalmatia_feeds = [
            "https://www.dalmacijanews.hr/feed",
            "https://www.dalmacijadanas.hr/feed",
            "https://dalmatinskiportal.hr/rss",
        ]
        self.apple_ai_feeds = [
            "https://techcrunch.com/feed/",
            "https://9to5mac.com/feed/",
            "https://www.techradar.com/rss",
            "https://www.cnet.com/rss/news/",
            "https://www.economist.com/science-and-technology/rss.xml",
            "https://www.artificialintelligence-news.com/feed/",
        ]

    def collect_feeds(self, feeds):
        print(f"Collecting news from {len(feeds)} feeds...")
        articles = []
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]: # Limit to 5 per feed to avoid overload
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if 'summary' in entry else ''
                    })
            except Exception as e:
                print(f"Error collecting from {feed_url}: {e}")
        return articles

    def collect_world_news(self):
        return self.collect_feeds(self.world_feeds)

    def collect_nba_news(self):
        return self.collect_feeds(self.nba_feeds)

    def collect_croatian_news(self):
        # Collect more articles per feed to give LLM a good pool
        print(f"Collecting Croatian news from {len(self.croatian_feeds)} feeds...")
        articles = []
        for feed_url in self.croatian_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]: # Limit to 10 per feed
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if 'summary' in entry else ''
                    })
            except Exception as e:
                print(f"Error collecting from {feed_url}: {e}")
        return articles

    def collect_dalmatia_news(self):
        print(f"Collecting Dalmatia news from {len(self.dalmatia_feeds)} feeds...")
        articles = []
        for feed_url in self.dalmatia_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if 'summary' in entry else ''
                    })
            except Exception as e:
                print(f"Error collecting from {feed_url}: {e}")
        return articles

    def collect_apple_ai_news(self):
        print(f"Collecting Apple & AI news from {len(self.apple_ai_feeds)} feeds...")
        return self.collect_feeds(self.apple_ai_feeds)

class NewsSummarizer:
    def __init__(self):
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt')
            nltk.download('punkt_tab')
        self.stemmer = Stemmer("english")
        self.summarizer = LsaSummarizer(self.stemmer)
        self.summarizer.stop_words = get_stop_words("english")

    def summarize(self, text, sentences_count=3):
        if not text:
            return "No content to summarize."
        
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary_sentences = self.summarizer(parser.document, sentences_count)
        
        summary = " ".join([str(s) for s in summary_sentences])
        return summary

# --- Email Service ---
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.environ.get("EMAIL_USER")
        self.email_password = os.environ.get("EMAIL_PASSWORD")
        self.recipient = os.environ.get("RECIPIENT_EMAIL", "dario.caric@gmail.com")

    def send_email(self, subject, body, images=None):
        if not self.email_user or not self.email_password:
            print("Email credentials not set. Skipping email.")
            return

        msg = MIMEMultipart('related') # Changed to related for embedded images
        msg['From'] = self.email_user
        msg['To'] = self.recipient
        msg['Subject'] = subject

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        msg_alternative.attach(MIMEText(body, 'html'))

        # Attach images
        if images:
            from email.mime.image import MIMEImage
            for img_id, img_data in images.items():
                image = MIMEImage(img_data.read())
                image.add_header('Content-ID', f'<{img_id}>')
                msg.attach(image)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.recipient, text)
            server.quit()
            print(f"Email sent to {self.recipient}")
        except Exception as e:
            print(f"Failed to send email: {e}")

# --- Scheduler ---
import schedule
import time
import threading

def generate_and_send_report():
    print("Generating scheduled report...")
    collector = NewsCollector()
    # summarizer = NewsSummarizer() # Replaced by LLM
    llm_summarizer = LLMSummarizer()
    score_collector = NBAScoreCollector()
    
    # 1. World News
    world_articles = collector.collect_world_news()
    world_summary = llm_summarizer.summarize_world_news(world_articles)
    
    html_content = "<h1>World News</h1>"
    html_content += f"<p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    
    # LLM Summary Section
    html_content += "<div style='background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    html_content += "<h3>🌍 AI Summary</h3>"
    html_content += f"<p>{world_summary}</p>"
    #html_content += "</div>"
    
    # World News Links in Light Blue Box
    #html_content += "<div style='background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    for article in world_articles:
        html_content += f"<h4><a href='{article['link']}'>{article['title']}</a></h4>"
    html_content += "</div>"
        # html_content += f"<p>{article['summary']}</p>" # Optional: keep original snippets? User said "below titles", maybe implies keeping them.
        # Let's keep titles clean and just rely on the AI summary for the "big picture", 
        # but user said "summarize all World News below titles". 
        # I will keep the list of titles/links for reference.

    # 2. Croatian News
    html_content += "<h1>Croatian News</h1>"
    cro_articles = collector.collect_croatian_news()
    cro_curated = llm_summarizer.curate_croatian_news(cro_articles)
    
    html_content += "<div style='background-color: #fffaf0; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    html_content += "<h3>🇭🇷 Najvažnije Vijesti (Hrvatska)</h3>"
    html_content += f"{cro_curated}"
    html_content += "</div>"

    # 3. Dalmatia News
    html_content += "<h1>Dalmatia News</h1>"
    dal_articles = collector.collect_dalmatia_news()
    dal_curated = llm_summarizer.curate_dalmatia_news(dal_articles)
    hajduk_game_info = llm_summarizer.get_next_hajduk_game()
    
    html_content += "<div style='background-color: #e0f7fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    html_content += "<h3>🌊 Najvažnije Vijesti (Dalmacija)</h3>"
    html_content += f"{hajduk_game_info}"
    html_content += "<hr style='border: 0; border-top: 1px solid #ccc; margin: 15px 0;'>"
    html_content += f"{dal_curated}"
    html_content += "</div>"

    # 4. Apple & AI News
    html_content += "<h1>Apple & AI News</h1>"
    apple_ai_articles = collector.collect_apple_ai_news()
    apple_ai_curated = llm_summarizer.curate_apple_ai_news(apple_ai_articles)
    
    html_content += "<div style='background-color: #f3e5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    html_content += "<h3>🍎 Apple & AI Highlights</h3>"
    html_content += f"{apple_ai_curated}"
    html_content += "</div>"

    # 5. NBA News
    html_content += "<h1>NBA News</h1>"
    
    # Start NBA Container
    html_content += "<div style='background-color: #fff8e1; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    
    nba_articles = collector.collect_nba_news()
    # Using world news summarizer for now as it's generic enough, or could add specific NBA one
    nba_summary = llm_summarizer.summarize_world_news(nba_articles)
    
    html_content += "<h3>🏀 NBA Updates</h3>"
    html_content += f"<p>{nba_summary}</p>"
    html_content += "<br>"

    # 6. NBA Scores Table
    scores = score_collector.get_last_nights_scores()
    
    # NBA Trends Analysis (using whatever recent data we have)
    weekly_scores = score_collector.get_weekly_scores()
    nba_trends = llm_summarizer.analyze_nba_trends(weekly_scores)
    
    html_content += "<h3>🏀 AI Performance Analysis</h3>"
    html_content += f"<p>{nba_trends}</p>"
    html_content += "<br>"

    if scores:
        html_content += "<h2>NBA Scores</h2>"
        html_content += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%; background-color: white;'>"
        html_content += "<tr style='background-color: #f2f2f2;'><th>Matchup</th><th>Score</th><th>Status</th></tr>"
        for game in scores:
            html_content += f"<tr><td>{game['matchup']}</td><td>{game['score']}</td><td>{game['status']}</td></tr>"
        html_content += "</table>" # Close the table tag
        
    html_content += "<br>"
    html_content += "<h3>Latest Headlines</h3>"
    for article in nba_articles:
         html_content += f"<h4><a href='{article['link']}'>{article['title']}</a></h4>"
         
    html_content += "</div>" # Close NBA Container

    # 7. Stock Portfolio
    html_content += "<h1>Stock Portfolio</h1>"
    stock_collector = StockCollector() # Re-initialize if not already in scope, or ensure it's available
    stock_data = stock_collector.get_stock_data()
    
    # Calculate Total Capital
    portfolio_manager = PortfolioManager() # Re-initialize if not already in scope, or ensure it's available
    total_capital = portfolio_manager.calculate_total_capital(stock_data)
    
    # Update History (Persistence)
    history = portfolio_manager.update_history(total_capital)
    
    # Initialize GraphGenerator
    graph_generator = GraphGenerator()
    images = {}
    
    html_content += "<div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>"
    html_content += "<h3>💰 Portfolio Overview</h3>"
    html_content += f"<h2>Total Capital: ${total_capital:,.2f}</h2>"
    
    html_content += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>"
    for ticker, data in stock_data.items():
        price = data['current_price']
        change = data['change']
        pct = (change / (price - change)) * 100 if (price - change) != 0 else 0
        
        arrow = "🟢 ▲" if change >= 0 else "🔴 ▼"
        color = "green" if change >= 0 else "red"
        
        # Generate graph
        img_buf = graph_generator.generate_stock_chart(ticker, data['history'])
        img_id = f"chart_{ticker}"
        images[img_id] = img_buf
        
        html_content += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                <h3>{ticker} {arrow}</h3>
                <p style="font-size: 1.2em; font-weight: bold;">${price:.2f}</p>
                <p style="color: {color};">{change:+.2f} ({pct:+.2f}%)</p>
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                <img src="cid:{img_id}" alt="{ticker} Chart" style="width: 300px; height: auto;">
            </td>
        </tr>
        """
    html_content += "</table>"
    
    # Total Capital
    # Determine arrow for total capital (compare to yesterday if available, else just show value)
    capital_arrow = ""
    if len(history) > 1:
        prev_total = history[-2]['total']
        if total_capital >= prev_total:
            capital_arrow = "🟢 ▲"
        else:
            capital_arrow = "🔴 ▼"
            
    html_content += f"<h2>Total Capital: ${total_capital:.2f} {capital_arrow}</h2>"
    
    # Portfolio Graph
    portfolio_img_buf = graph_generator.generate_portfolio_chart(history)
    if portfolio_img_buf:
        img_id = "chart_portfolio"
        images[img_id] = portfolio_img_buf
        html_content += f'<img src="cid:{img_id}" alt="Portfolio History" style="width: 100%; max-width: 600px; height: auto;">'
    elif not portfolio_manager.bucket_name:
        html_content += "<p><i>(Persistence not enabled. Set BUCKET_NAME to see history graph)</i></p>"

    # AI Market Analysis
    stock_analysis = llm_summarizer.analyze_stock_market()
    html_content += "<hr style='border: 0; border-top: 1px solid #ccc; margin: 15px 0;'>"
    html_content += "<h3>🤖 AI Market Analysis</h3>"
    html_content += f"{stock_analysis}"
    
    html_content += "</div>" # Close Stock Portfolio div
    html_content += "</body></html>"

    email_service = EmailService()
    subject = f"DARIO NEWS - {datetime.now().strftime('%Y-%m-%d')}"
    email_service.send_email(subject, html_content, images)

def run_scheduler():
    # Schedule for 8am and 7pm CET
    # Note: schedule library uses system time. If running in Docker, set TZ env var.
    # Alternatively, we can check time in the loop, but let's assume TZ is set correctly or handle it.
    # For simplicity in this MVP, we schedule at the specific times.
    
    cet_tz = pytz.timezone("Europe/Paris")
    schedule.every().day.at("08:00", cet_tz).do(generate_and_send_report)
    schedule.every().day.at("19:00", cet_tz).do(generate_and_send_report)
    
    print("Scheduler started. Tasks scheduled for 08:00 and 19:00.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- FastAPI App ---
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    yield
    # Shutdown (nothing specific needed for thread as it is daemon)

app = FastAPI(lifespan=lifespan)

@app.get("/")
def get_news():
    collector = NewsCollector()
    summarizer = NewsSummarizer()
    
    world_articles = collector.collect_world_news()
    nba_articles = collector.collect_nba_news()
    
    # Combine for simple JSON response
    all_articles = world_articles + nba_articles
    
    results = []
    for article in all_articles:
        content = article['summary']
        import re
        clean_content = re.sub('<[^<]+?>', '', content)
        summary = summarizer.summarize(clean_content)
        
        results.append({
            "title": article['title'],
            "link": article['link'],
            "summary": summary
        })
    
    return {"count": len(results), "articles": results}

@app.post("/test-email")
def trigger_email():
    """Manually trigger the email report for testing."""
    try:
        generate_and_send_report()
        return {"status": "Email triggered"}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error triggering email: {error_details}")
        return {"status": "Error", "message": str(e), "details": error_details}

def main():
    # For local CLI testing
    collector = NewsCollector()
    summarizer = NewsSummarizer()
    score_collector = NBAScoreCollector()
    
    print("--- WORLD NEWS ---")
    world_articles = collector.collect_world_news()
    for article in world_articles:
        print(f"TITLE: {article['title']}")
    
    print("\n--- CROATIAN NEWS ---")
    cro_articles = collector.collect_croatian_news()
    print(f"Collected {len(cro_articles)} articles.")
    for article in cro_articles[:3]:
        print(f"TITLE: {article['title']}")

    print("\n--- DALMATIA NEWS ---")
    dal_articles = collector.collect_dalmatia_news()
    print(f"Collected {len(dal_articles)} articles.")
    for article in dal_articles[:3]:
        print(f"TITLE: {article['title']}")

    print("\n--- NBA SCORES (Last Night) ---")
    scores = score_collector.get_last_nights_scores()
    if scores:
        for game in scores:
            print(f"{game['matchup']}: {game['score']} ({game['status']})")
    else:
        print("No games found.")

    print("\n--- NBA NEWS ---")
    nba_articles = collector.collect_nba_news()
    for article in nba_articles:
        print(f"TITLE: {article['title']}")

    print("\n--- STOCK PORTFOLIO ---")
    stock_data = score_collector = StockCollector().get_stock_data()
    for ticker, data in stock_data.items():
        print(f"{ticker}: ${data['current_price']:.2f} ({data['change']:+.2f})")
    
    pm = PortfolioManager()
    total = pm.calculate_total_capital(stock_data)
    print(f"Total Capital: ${total:.2f}")
    if not pm.bucket_name:
        print("(Persistence disabled: BUCKET_NAME not set)")

if __name__ == "__main__":
    # Check if running as script or API
    import sys
    if "serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        main()
