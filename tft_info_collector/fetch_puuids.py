import argparse
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

LEAGUE_ENDPOINTS = [
    "challenger",
    "grandmaster",
    "master"
]

BASE_URL = "https://{platform}.api.riotgames.com/tft/league/v1/{endpoint}"

HEADERS = {
    "X-Riot-Token": API_KEY
}


def fetch_league(platform, endpoint):
    url = BASE_URL.format(platform=platform, endpoint=endpoint)
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def collect_players(platform, max_count):
    collected = []

    for endpoint in LEAGUE_ENDPOINTS:
        print(f"Fetching: {endpoint.upper()}")

        data = fetch_league(platform, endpoint)
        entries = data.get("entries", [])

        for item in entries:
            collected.append({
                "tier": data.get("tier"),
                "rank": item.get("rank"),
                "leaguePoints": item.get("leaguePoints"),
                "wins": item.get("wins"),
                "losses": item.get("losses"),
                "freshBlood": item.get("freshBlood"),
                "veteran": item.get("veteran"),
                "hotStreak": item.get("hotStreak"),
                "inactive": item.get("inactive"),
                "puuid": item.get("puuid"),
                "summonerId": item.get("summonerId")
            })

            if len(collected) >= max_count:
                return collected

    return collected


def main():
    parser = argparse.ArgumentParser(description="Fetch high-elo TFT players")
    parser.add_argument("--platform", required=True, help="e.g., na1, euw1, kr, jp1 etc.")
    parser.add_argument("--count", type=int, default=500, help="Number of players to retrieve")
    parser.add_argument("--out", default="data/raw/players.json", help="Where to save JSON")

    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: No RIOT_API_KEY found in .env")
        return

    players = collect_players(args.platform, args.count)

    import json
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(players, f, indent=2)

    print(f"Saved {len(players)} players → {args.out}")


if __name__ == "__main__":
    main()