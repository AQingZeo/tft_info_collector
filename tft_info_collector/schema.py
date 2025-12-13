"""
Canonical cleaning schemas for TFT match data.

These schemas define how raw Riot match data can be
normalized into CSV-friendly tables.

They are NOT enforced automatically — they serve as
contracts for cleaners and downstream analytics.
"""

from typing import TypedDict, List


# -------------------------
# Core / Default Schemas
# -------------------------

class MatchRow(TypedDict):
    match_id: str
    region: str
    game_datetime: int
    game_length: float
    game_version: str
    queue_id: int
    set_number: int


class ParticipantRow(TypedDict):
    match_id: str
    puuid: str
    placement: int
    level: int
    gold_left: int
    win: bool


class UnitRow(TypedDict):
    match_id: str
    puuid: str
    unit_id: str
    star_level: int
    rarity: int
    items: str  # semicolon-separated item names


class TraitRow(TypedDict):
    match_id: str
    puuid: str
    trait_id: str
    tier_current: int
    style: int
    num_units: int


class AugmentRow(TypedDict):
    match_id: str
    puuid: str
    augment_slot: int
    augment_id: str
    augment_name: str


# -------------------------
# Identity / Cosmetic Schemas
# -------------------------

class ParticipantProfileRow(TypedDict):
    puuid: str
    riot_id_game_name: str
    riot_id_tagline: str
    region: str
    companion_species: str
    companion_skin_id: int
    companion_item_id: int