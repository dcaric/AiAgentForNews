from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams

def check_scores(date_str):
    print(f"Checking scores for {date_str}...")
    try:
        board = scoreboardv2.ScoreboardV2(game_date=date_str)
        games = board.game_header.get_dict()['data']
        line_score = board.line_score.get_dict()['data']
        
        # Map headers
        ls_headers = board.line_score.get_dict()['headers']
        pts_idx = ls_headers.index('PTS')
        team_id_idx = ls_headers.index('TEAM_ID')
        game_id_idx = ls_headers.index('GAME_ID')
        
        for game in games:
            game_id = game[2]
            home_team_id = game[6]
            visitor_team_id = game[7]
            
            # Resolve Team Names
            home_team_info = teams.find_team_name_by_id(home_team_id)
            visitor_team_info = teams.find_team_name_by_id(visitor_team_id)
            home_abbr = home_team_info['abbreviation'] if home_team_info else "Home"
            visitor_abbr = visitor_team_info['abbreviation'] if visitor_team_info else "Visitor"
            
            home_score = "N/A"
            visitor_score = "N/A"
            
            if line_score:
                for line in line_score:
                    if line[game_id_idx] == game_id:
                        if line[team_id_idx] == home_team_id:
                            home_score = line[pts_idx]
                        elif line[team_id_idx] == visitor_team_id:
                            visitor_score = line[pts_idx]
            
            print(f"{visitor_abbr} vs {home_abbr}: {visitor_score} - {home_score}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_scores('2024-11-22')
