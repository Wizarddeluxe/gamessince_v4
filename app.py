from flask import Flask, render_template
from get_home_runs import get_season_home_run_hitters, get_hr_stats, get_leaderboard
import os

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
