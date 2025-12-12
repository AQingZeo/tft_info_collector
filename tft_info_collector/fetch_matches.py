import json
import asyncio
from pathlib import Path
from typing import Iterable, Union

from .riot import RiotAPI
from .utils.routing import platform_to_region


async def fetch_matches(
    file_path: Path,
    limit: int = 20,
    out_dir: Path = Path("data/raw/matches"),
    sleep_ids: float = 0.2,
    sleep_matches: float = 0.3,
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
    out_dir.mkdir(parents=True, exist_ok=True)

    all_match_ids: set[str] = set()

    # ----------------------------------------
    # 1. Fetch match IDs
    # ----------------------------------------
    for puuid in puuids:
        try:
            match_ids = await api.get(
                f"/tft/match/v1/matches/by-puuid/{puuid}/ids",
                params={"count": limit},
            )
            all_match_ids.update(match_ids)
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
            data = await api.get(f"/tft/match/v1/matches/{match_id}")
            out_file.write_text(json.dumps(data))
            results.append(data)
        except Exception as e:
            print(f"[warn] failed to fetch match {match_id}: {e}")

        await asyncio.sleep(sleep_matches)

    return results