import requests, json, os
from datetime import datetime

def get_season_home_run_hitters():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        cache_path = os.path.join(BASE_DIR, "data", "season_hr_cache.json")
        with open(cache_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No HR cache file found — returning empty list")
        return []

def get_hr_stats(player_id):
    season = datetime.now().year
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&season={season}"
    logs = requests.get(url).json()
    games = logs["stats"][0]["splits"]
    game_streak = 0
    ab_streak = 0

    for game in reversed(games[:-1]):
        ab_streak += int(game["stat"].get("atBats", 0))
        game_streak += 1
        if game["stat"]["homeRuns"] != "0":
            break

    return game_streak, ab_streak

def get_leaderboard():
    season = datetime.now().year
    url = f"https://statsapi.mlb.com/api/v1/stats/leaders?season={season}&leagueId=103,104&sportId=1&statGroup=hitting"
    response = requests.get(url).json()

    if "leagueLeaders" not in response:
        print("⚠️ leagueLeaders not in response:", response)
        return []

    stats_to_get = ["homeRuns", "hits", "rbi", "baseOnBalls"]
    leaderboard = []

    for entry in response["leagueLeaders"]:
        stat_type = entry["leaderCategory"]
        if stat_type not in stats_to_get:
            continue
        for player in entry["leaders"]:
            pid = player["person"]["id"]
            name = player["person"]["fullName"]
            value = player["value"]
            found = next((x for x in leaderboard if x["id"] == pid), None)
            if not found:
                leaderboard.append({"id": pid, "name": name})
            for x in leaderboard:
                if x["id"] == pid:
                    x[stat_type] = int(float(value))

    for p in leaderboard:
        for stat in stats_to_get:
            if stat not in p:
                p[stat] = 0

    return sorted(leaderboard, key=lambda x: x["homeRuns"], reverse=True)
