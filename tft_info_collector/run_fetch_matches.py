import json
import asyncio
from tft_info_collector.fetch_matches import fetch_matches

LADDER_JSON = "data/raw/na_top500.json"   # change if needed
REGION = "americas"
MATCHES_PER_PLAYER = 10

async def main():
    with open(LADDER_JSON, "r") as f:
        players = json.load(f)

    await fetch_matches(
        region=REGION,
        players=players,
        limit=MATCHES_PER_PLAYER
    )

if __name__ == "__main__":
    asyncio.run(main())