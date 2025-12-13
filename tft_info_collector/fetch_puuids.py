import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
if not API_KEY:
    raise RuntimeError("RIOT_API_KEY not set")

LEAGUE_ENDPOINTS = ["challenger", "grandmaster", "master"]

BASE_URL = "https://{platform}.api.riotgames.com/tft/league/v1/{endpoint}"
HEADERS = {"X-Riot-Token": API_KEY}


def fetch_league(platform: str, endpoint: str) -> Dict:
    url = BASE_URL.format(platform=platform, endpoint=endpoint)
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def collect_players(platform: str, max_count: int) -> List[Dict]:
    collected: List[Dict] = []
    counts_by_rank: Dict[str, int] = {}

    for endpoint in LEAGUE_ENDPOINTS:
        data = fetch_league(platform, endpoint)
        entries = data.get("entries", [])
        counts_by_rank[endpoint] = 0

        for entry in entries:
            collected.append(entry)
            counts_by_rank[endpoint] += 1

            if len(collected) >= max_count:
                break

        print(f"{endpoint.capitalize()}: {counts_by_rank[endpoint]} players retrieved")

        if len(collected) >= max_count:
            break

    print(f"Total players retrieved: {len(collected)}")
    return collected