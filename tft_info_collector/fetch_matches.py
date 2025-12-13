import json
import asyncio
import time
from pathlib import Path
from typing import Iterable, Union, Optional, Dict

from .riot import RiotAPI
from .utils.routing import platform_to_region

LOG_PATH = Path("data/raw/match_fetch_log.json")


async def fetch_matches(
    file_path: Path,
    limit: int = 20,
    out_dir: Path = Path("data/raw/matches"),
    sleep_ids: float = 0.6,
    sleep_matches: float = 1.2,
):
    """
    Fetch TFT match data for a list of players.

    Parameters
    ----------
    ids_path : Path
        Path to JSON file containing player IDs and platform
    limit : int
        Number of matches to fetch per player
    out_dir : Path
        Directory to store raw match JSON files
    sleep_ids : float
        Delay between match-id requests
    sleep_matches : float
        Delay between match-detail requests
    """

    raw = json.loads(file_path.read_text())

    if LOG_PATH.exists():
        fetch_log = json.loads(LOG_PATH.read_text())
    else:
        fetch_log = {}

    if not isinstance(raw, dict):
        raise ValueError(
            "IDs file must be a JSON object with keys: 'platform' and 'players'."
        )

    platform = raw.get("platform")
    players = raw.get("players")

    if not platform or not players:
        raise ValueError(
            "IDs JSON must include both 'platform' and 'players' fields."
        )

    region = platform_to_region(platform)

    puuids: list[str] = []
    for p in players:
        if isinstance(p, str):
            puuids.append(p)
        elif isinstance(p, dict) and "puuid" in p:
            puuids.append(p["puuid"])

    puuids = list(dict.fromkeys(puuids))  # de-duplicate, preserve order

    api = RiotAPI(region)

    async def safe_get(
        url: str,
        params: Optional[Dict] = None,
        retries: int = 5,
    ):
        for attempt in range(retries):
            try:
                return await api.get(url, params=params)
            except Exception as e:
                msg = str(e)
                if "429" in msg:
                    wait = max(5, 2 ** attempt)
                    print(f"[rate-limit] hit 429, sleeping {wait}s (retry {attempt+1}/{retries})")
                    await asyncio.sleep(wait)
                    continue
                raise
        raise RuntimeError("Exceeded retry limit due to rate limiting")

    out_dir.mkdir(parents=True, exist_ok=True)

    all_match_ids: set[str] = set()

    # ----------------------------------------
    # 1. Fetch match IDs
    # ----------------------------------------
    for puuid in puuids:
        logged = fetch_log.get(puuid, {})
        logged_ids = set(logged.get("fetched_match_ids", []))

        if len(logged_ids) >= limit:
            print(f"[skip] {puuid} already fetched ({len(logged_ids)})")
            continue

        try:
            match_ids = await safe_get(
                f"/tft/match/v1/matches/by-puuid/{puuid}/ids",
                params={"count": limit},
            )
            new_ids = [mid for mid in match_ids if mid not in logged_ids]

            fetch_log.setdefault(puuid, {
                "platform": platform,
                "fetched_match_ids": []
            })["fetched_match_ids"].extend(new_ids)

            all_match_ids.update(new_ids)

            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            LOG_PATH.write_text(json.dumps(fetch_log, indent=2))

        except Exception as e:
            print(f"[warn] failed to fetch match IDs for {puuid}: {e}")

        await asyncio.sleep(sleep_ids)

    # ----------------------------------------
    # 2. Fetch match details (cached)
    # ----------------------------------------
    results: list[dict] = []

    for match_id in all_match_ids:
        out_file = out_dir / f"{match_id}.json"

        if out_file.exists():
            try:
                results.append(json.loads(out_file.read_text()))
                continue
            except Exception:
                pass  # corrupted cache → refetch

        try:
            data = await safe_get(f"/tft/match/v1/matches/{match_id}")
            out_file.write_text(json.dumps(data))
            results.append(data)

            for p in data.get("metadata", {}).get("participants", []):
                if p in fetch_log:
                    if match_id not in fetch_log[p]["fetched_match_ids"]:
                        fetch_log[p]["fetched_match_ids"].append(match_id)

            LOG_PATH.write_text(json.dumps(fetch_log, indent=2))

        except Exception as e:
            print(f"[warn] failed to fetch match {match_id}: {e}")

        await asyncio.sleep(sleep_matches)

    return results