import requests
import json

def check_cdn_scores():
    url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    try:
        response = requests.get(url)
        data = response.json()
        print(f"Date: {data['scoreboard']['gameDate']}")
        for game in data['scoreboard']['games']:
            print(f"{game['awayTeam']['teamTricode']} vs {game['homeTeam']['teamTricode']}: {game['awayTeam']['score']} - {game['homeTeam']['score']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cdn_scores()
