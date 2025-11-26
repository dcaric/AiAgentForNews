import requests
from datetime import datetime, timedelta
import time

def fetch_history():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com'
    }
    
    # Real time is 2024. System is 2025.
    real_now = datetime.now().replace(year=datetime.now().year - 1)
    
    print(f"Fetching history starting from {real_now.strftime('%Y-%m-%d')} backwards...")
    
    for i in range(1, 4): # Try 3 days
        date = real_now - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d') # Format: YYYY-MM-DD for stats.nba.com usually works? Or MM/DD/YYYY?
        # ScoreboardV2 uses YYYY-MM-DD usually.
        
        params = {
            'GameDate': date_str,
            'LeagueID': '00',
            'DayOffset': '0'
        }
        
        url = 'https://stats.nba.com/stats/scoreboardv2'
        try:
            print(f"Fetching {date_str}...")
            resp = requests.get(url, headers=headers, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            # Check if we got games
            games = data['resultSets'][0]['rowSet']
            print(f"Found {len(games)} games for {date_str}")
        except Exception as e:
            print(f"Failed for {date_str}: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    fetch_history()
