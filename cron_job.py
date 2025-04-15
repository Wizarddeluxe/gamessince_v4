import requests, json, os
from datetime import datetime, timedelta

def get_all_home_run_hitters():
    season_start = datetime(datetime.now().year, 3, 28)
    today = datetime.now()
    game_dates = [(season_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((today - season_start).days + 1)]

    home_run_data = {}

    print(f"[INFO] Checking {len(game_dates)} dates from {season_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

    for date in game_dates:
        try:
            schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
            schedule = requests.get(schedule_url).json()

            game_count = 0
            for day in schedule.get("dates", []):
                for game in day.get("games", []):
                    if game["status"]["abstractGameState"] != "Final":
                        continue
                    game_pk = game["gamePk"]
                    game_count += 1
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
            print(f"[INFO] {date}: {game_count} games processed")

        except Exception as e:
            print(f"[ERROR] {date}: {e}")

    os.makedirs("data", exist_ok=True)
    with open("data/season_hr_cache.json", "w") as f:
        json.dump(list(home_run_data.values()), f, indent=2)

    print(f"[SUCCESS] Wrote {len(home_run_data)} HR hitters to data/season_hr_cache.json")
    if home_run_data:
        sample = list(home_run_data.values())[0]
        print(f"[SAMPLE] {sample}")

if __name__ == "__main__":
    get_all_home_run_hitters()
