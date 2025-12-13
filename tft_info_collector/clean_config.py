"""
clean_config.py

Single source of truth for:
1) what tables exist and how to extract them from Riot match JSON (CLEAN_SCHEMAS)
2) which columns to keep for each preset (CLEAN_PRESETS)

Notes:
- Paths support dot-notation and list expansion with [] (e.g. info.participants[].units[])
- Use "join" to collapse lists into a single CSV cell.
"""

from __future__ import annotations

# ----------------------------
# 1) Extraction schema (no hard-coding in cleaner)
# ----------------------------

CLEAN_SCHEMAS = {
    # One row per match
    "match": {
        "path": "",  # root match object
        "fields": {
            "match_id": "metadata.match_id",
            "region": "__region__",  # optional: filled by cleaner if you pass region; otherwise blank
            "game_datetime": "info.game_datetime",
            "game_length": "info.game_length",
            "queue_id": "info.queue_id",
            "set_number": "info.tft_set_number",
            "set_name": "info.tft_set_core_name",
            "game_version": "info.game_version",
        },
    },

    # One row per participant
    "participant": {
        "path": "info.participants[]",
        "fields": {
            "match_id": {"from_root": "metadata.match_id"},
            "region": "__region__",
            "puuid": "puuid",
            "placement": "placement",
            "level": "level",
            "last_round": "last_round",
        },
    },

    # One row per unit (participant × unit)
    "unit": {
        "path": "info.participants[].units[]",
        "fields": {
            "match_id": {"from_root": "metadata.match_id"},
            "puuid": {"from_parent": "puuid"},
            "unit_id": "character_id",
            "star_level": "tier",
            "rarity": "rarity",
            "items": {"join": {"path": "itemNames", "sep": ";"}},  # list -> "a;b;c"
        },
    },

    # One row per trait (participant × trait)
    "trait": {
        "path": "info.participants[].traits[]",
        "fields": {
            "match_id": {"from_root": "metadata.match_id"},
            "puuid": {"from_parent": "puuid"},
            "trait_id": "name",
            "num_units": "num_units",
            "style": "style",
            "tier_current": "tier_current",
            "tier_total": "tier_total",
        },
    },
}

# ----------------------------
# 2) Presets (what to keep in output)
# ----------------------------

CLEAN_PRESETS = {
    "default": {
        "match": [
            "match_id",
            "game_datetime",
            "game_length",
            "queue_id",
            "set_number",
        ],
        "participant": [
            "match_id",
            "puuid",
            "placement",
            "level",
            "last_round",
        ],
        "unit": [
            "match_id",
            "puuid",
            "unit_id",
            "star_level",
            "rarity",
            "items",
        ],
        "trait": [
            "match_id",
            "puuid",
            "trait_id",
            "num_units",
            "tier_current",
        ],
    },

    # Full data dump (analytics / research)
    "full": {
        "match": "__all__",
        "participant": "__all__",
        "unit": "__all__",
        "trait": "__all__",
    },
}