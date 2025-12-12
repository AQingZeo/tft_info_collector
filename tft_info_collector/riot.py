import httpx
from .config import settings

class RiotAPI:
    def __init__(self, region: str):
        self.region = region
        self.base = f"https://{region}.api.riotgames.com"
        self.key = settings.RIOT_API_KEY

    async def get(self, endpoint: str, params: dict = None):
        headers = {"X-Riot-Token": self.key}
        async with httpx.AsyncClient() as client:
            r = await client.get(self.base + endpoint, headers=headers, params=params)
            r.raise_for_status()
            return r.json()