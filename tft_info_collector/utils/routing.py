"""
Riot API routing helpers.

Purpose:
- Convert platform routing (e.g. na1, euw1) to regional routing
  used by match-v1 endpoints (americas, europe, asia).
"""

PLATFORM_TO_REGION = {
    # Americas
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "oc1": "americas",

    # Europe
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",

    # Asia
    "kr": "asia",
    "jp1": "asia",
}


def platform_to_region(platform: str) -> str:
    """
    Convert a platform routing value (e.g. na1) to a regional routing value.

    Raises:
        ValueError if platform is unknown.
    """
    platform = platform.lower()

    if platform not in PLATFORM_TO_REGION:
        raise ValueError(
            f"Unknown platform '{platform}'. "
            f"Expected one of: {sorted(PLATFORM_TO_REGION.keys())}"
        )

    return PLATFORM_TO_REGION[platform]