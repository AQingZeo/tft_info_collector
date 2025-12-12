import typer
import asyncio
from rich import print
from .fetch_puuids import fetch_high_elo_puuids
from .fetch_matches import fetch_matches

app = typer.Typer()

@app.command()
def fetch(region: str = "na1", count: int = 500):
    """Fetch high-elo PUUIDs"""
    puuids = asyncio.run(fetch_high_elo_puuids(region, count))
    print(f"[green]Saved {len(puuids)} PUUIDs!")

@app.command("download-matches")
def download_matches(region: str = "na1", limit: int = 20):
    """Download recent matches for stored PUUIDs"""
    import json, pathlib
    puuid_path = pathlib.Path(f"data/puuids/{region}.json")
    puuids = json.loads(puuid_path.read_text())
    results = asyncio.run(fetch_matches(region, puuids, limit))
    print(f"[green]Downloaded {len(results)} matches.")

if __name__ == "__main__":
    app()