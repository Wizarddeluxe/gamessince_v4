import requests, json, os

def get_fixed_home_run_hitters():
    date = "2025-04-13"
    home_run_data = {}

    print(f"[INFO] Fetching HRs for fixed date: {date}")
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    schedule = requests.get(schedule_url).json()

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
                    pid = player["id"]
                    name = player["fullName"]
                    home_run_data[pid] = {
                        "id": pid,
                        "name": name,
                        "last_hr_date": date
                    }

    os.makedirs("data", exist_ok=True)
    with open("data/season_hr_cache.json", "w") as f:
        json.dump(list(home_run_data.values()), f, indent=2)

    print(f"[SUCCESS] Cached {len(home_run_data)} HR hitters from {date}")

if __name__ == "__main__":
    get_fixed_home_run_hitters()
