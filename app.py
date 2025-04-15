from flask import Flask, render_template
from get_home_runs import get_season_home_run_hitters, get_hr_stats, get_leaderboard
import os
from datetime import datetime
import requests

app = Flask(__name__)

@app.route("/")
def index():
    players = get_season_home_run_hitters()
    for p in players:
        try:
            streak_games, streak_abs = get_hr_stats(p["id"])
            p["games_since_hr"] = streak_games
            p["abs_since_hr"] = streak_abs
        except Exception as e:
            print(f"⚠️ Error fetching stats for {p['name']}: {e}")
            p["games_since_hr"] = "-"
            p["abs_since_hr"] = "-"
    leaderboard = get_leaderboard()
    return render_template("index.html", players=players, leaderboard=leaderboard)

@app.route("/debug/hr")
def debug_home_runs():
    date = "2025-04-13"
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    schedule = requests.get(schedule_url).json()
    home_run_names = []
    for day in schedule.get("dates", []):
        for game in day.get("games", []):
            if game["status"]["abstractGameState"] != "Final":
                continue
            game_pk = game["gamePk"]
            feed_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
            feed = requests.get(feed_url).json()
            for play in feed.get("liveData", {}).get("plays", {}).get("allPlays", []):
                if play["result"]["eventType"] == "home_run":
                    player = play["matchup"]["batter"]
                    home_run_names.append(player["fullName"])
    return {
        "date": date,
        "total_home_runs": len(home_run_names),
        "players": home_run_names
    }
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
