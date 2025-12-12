import json
import asyncio
from pathlib import Path
from .riot import RiotAPI


async def fetch_matches(region: str, players: list, limit: int = 20):
    """
    Fetch TFT matches for a list of players.

    `players` can be:
      - a list of PUUID strings
      - OR a list of dicts that contain a 'puuid' field
    """

    # Normalize input → list of puuids
    puuids = []
    for p in players:
        if isinstance(p, str):
            puuids.append(p)
        elif isinstance(p, dict) and "puuid" in p:
            puuids.append(p["puuid"])

    api = RiotAPI(region)
    out_dir = Path("data/matches_raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_match_ids = set()

    # ----------------------------------------
    # 1. Fetch match IDs for each PUUID
    # ----------------------------------------
    for puuid in puuids:
        try:
            match_ids = await api.get(
                f"/tft/match/v1/matches/by-puuid/{puuid}/ids",
                params={"count": limit}
            )
            for mid in match_ids:
                all_match_ids.add(mid)
        except Exception as e:
            print(f"Failed to fetch match IDs for {puuid}: {e}")

        await asyncio.sleep(0.2)

    # ----------------------------------------
    # 2. Fetch match details (with caching)
    # ----------------------------------------
    results = []

    for match_id in all_match_ids:
        out_file = out_dir / f"{match_id}.json"

        # Reuse cached match if exists
        if out_file.exists():
            try:
                results.append(json.loads(out_file.read_text()))
                continue
            except Exception:
                pass  # fall through and re-fetch if cache is corrupted

        try:
            data = await api.get(f"/tft/match/v1/matches/{match_id}")
            out_file.write_text(json.dumps(data))
            results.append(data)
        except Exception as e:
            print(f"Failed to fetch match {match_id}: {e}")

        await asyncio.sleep(0.3)

    return results