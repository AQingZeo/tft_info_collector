import typer
from pathlib import Path
import json
import asyncio

from .fetch_puuids import collect_players
from .fetch_matches import fetch_matches

app = typer.Typer(help="TFT data collection CLI")


@app.command("fetch-ids")
def fetch_ids_cmd(
    platform: str = typer.Option(
        "na1", "--platform", "-p", help="Platform shard (na1, euw1, kr, etc)"
    ),
    count: int = typer.Option(
        500, "--count", "-c", help="Number of players to fetch"
    ),
    out: Path = typer.Option(
        Path("data/raw/players.json"),
        "--out",
        "-o",
        help="Output JSON path",
    ),
):
    """
    Fetch high-elo TFT player PUUIDs.
    """
    players = collect_players(platform, count)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "platform": platform,
        "players": players,
    }

    out.write_text(json.dumps(payload, indent=2))

    typer.echo(f"Saved {len(players)} players → {out}")


@app.command("fetch-matches")
def fetch_matches_cmd(
    file: Path = typer.Option(
        Path("data/raw/players.json"),
        "--file",
        "-f",
        help="Path to players JSON file (output of fetch-ids)",
    ),
    limit: int = typer.Option(
        20, "--limit", "-l", help="Matches per player"
    ),
):
    """
    Fetch raw match data for stored PUUIDs.
    """
    asyncio.run(
        fetch_matches(
            file_path=file,
            limit=limit,
        )
    )
    typer.echo("Finished fetching matches")


def main():
    app()