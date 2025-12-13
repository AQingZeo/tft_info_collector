from pathlib import Path
import json
import csv
from typing import Dict, List, Any, Union, Callable

from .clean_config import CLEAN_PRESETS, CLEAN_SCHEMAS


def _strip_prefix(value: str) -> str:
    """
    Normalize Riot-style identifiers by keeping only the suffix
    after the last underscore.

    Examples:
      TFT_Item_GuinsoosRageblade -> GuinsoosRageblade
      TFT14_Ahri -> Ahri
      TFT14_Trait_Sorcerer -> Sorcerer
    """
    if not value or not isinstance(value, str):
        return ""
    return value.rsplit("_", 1)[-1]


def _normalize_items(unit: dict) -> str:
    raw_items = unit.get("itemNames", [])
    if not isinstance(raw_items, list):
        return ""
    return ";".join(
        _strip_prefix(i) for i in raw_items if isinstance(i, str)
    )


def _filter_columns(rows: List[Dict], keep):
    if keep == "__all__":
        return rows
    if not rows:
        return rows
    return [
        {k: row.get(k) for k in keep}
        for row in rows
    ]


def _get_from_path(obj: Any, path: Union[str, List[str]]) -> List[Any]:
    """
    Traverse the obj according to the path, which can include list indicators '[]'.
    Returns a list of matching objects.
    """
    if isinstance(path, str):
        path = path.split(".")
    objs = [obj]
    for part in path:
        next_objs = []
        if part.endswith("[]"):
            key = part[:-2]
            for o in objs:
                val = o.get(key) if isinstance(o, dict) else None
                if isinstance(val, list):
                    next_objs.extend(val)
        else:
            key = part
            for o in objs:
                val = o.get(key) if isinstance(o, dict) else None
                if val is not None:
                    next_objs.append(val)
        objs = next_objs
        if not objs:
            break
    return objs


def _extract_rows(match: Dict, schema: Dict) -> List[Dict]:
    """
    Extract rows from a match dict according to the schema.
    schema keys:
      - path: dotted path string or list of strings to locate list of items
      - fields: dict of output column -> source field name or callable taking item and match
    """
    rows = []
    path = schema.get("path", "")
    fields = schema.get("fields", {})

    match_id = match.get("metadata", {}).get("match_id")

    # Handle participant-nested paths explicitly
    if isinstance(path, str):
        path_str = path
    else:
        path_str = ".".join(path)

    if path_str.startswith("info.participants[]"):
        participants = match.get("info", {}).get("participants", [])
        # Determine if we are extracting participants themselves, or nested units/traits
        if path_str == "info.participants[]":
            # Extract participant-level rows
            for participant in participants:
                row = {}
                for col, source in fields.items():
                    if col == "match_id":
                        row[col] = match_id
                        continue
                    if callable(source):
                        try:
                            row[col] = source(participant, match)
                        except Exception:
                            row[col] = None
                    elif isinstance(source, str):
                        if "." in source:
                            val = participant
                            for part in source.split("."):
                                if isinstance(val, dict):
                                    val = val.get(part)
                                else:
                                    val = None
                                    break
                            row[col] = val
                        else:
                            row[col] = participant.get(source)
                    else:
                        row[col] = None
                rows.append(row)
        elif path_str == "info.participants[].units[]":
            # Extract units nested inside participants, injecting participant context
            for participant in participants:
                puuid = participant.get("puuid")
                units = participant.get("units", [])
                for unit in units:
                    row = {}
                    for col, source in fields.items():
                        if col == "match_id":
                            row[col] = match_id
                            continue
                        if col == "puuid":
                            row[col] = puuid
                            continue
                        if col == "items":
                            row[col] = _normalize_items(unit)
                            continue
                        if callable(source):
                            try:
                                row[col] = source(unit, match)
                            except Exception:
                                row[col] = None
                        elif isinstance(source, str):
                            if "." in source:
                                val = unit
                                for part in source.split("."):
                                    if isinstance(val, dict):
                                        val = val.get(part)
                                    else:
                                        val = None
                                        break
                                if source in ("character_id", "name"):
                                    row[col] = _strip_prefix(val) if isinstance(val, str) else val
                                else:
                                    row[col] = val
                            else:
                                val = unit.get(source)
                                if source in ("character_id", "name"):
                                    row[col] = _strip_prefix(val) if isinstance(val, str) else val
                                else:
                                    row[col] = val
                        else:
                            row[col] = None
                    rows.append(row)
        elif path_str == "info.participants[].traits[]":
            # Extract traits nested inside participants, injecting participant context
            for participant in participants:
                puuid = participant.get("puuid")
                traits = participant.get("traits", [])
                for trait in traits:
                    row = {}
                    for col, source in fields.items():
                        if col == "match_id":
                            row[col] = match_id
                            continue
                        if col == "puuid":
                            row[col] = puuid
                            continue
                        if callable(source):
                            try:
                                row[col] = source(trait, match)
                            except Exception:
                                row[col] = None
                        elif isinstance(source, str):
                            if "." in source:
                                val = trait
                                for part in source.split("."):
                                    if isinstance(val, dict):
                                        val = val.get(part)
                                    else:
                                        val = None
                                        break
                                if source == "name":
                                    row[col] = _strip_prefix(val) if isinstance(val, str) else val
                                else:
                                    row[col] = val
                            else:
                                val = trait.get(source)
                                if source == "name":
                                    row[col] = _strip_prefix(val) if isinstance(val, str) else val
                                else:
                                    row[col] = val
                        else:
                            row[col] = None
                    rows.append(row)
        else:
            # For other participant nested paths, fallback to generic _get_from_path
            items = _get_from_path(match, path)
            if not items:
                return rows
            for item in items:
                row = {}
                for col, source in fields.items():
                    if col == "match_id":
                        row[col] = match_id
                        continue
                    if callable(source):
                        try:
                            row[col] = source(item, match)
                        except Exception:
                            row[col] = None
                    elif isinstance(source, str):
                        if "." in source:
                            val = item
                            for part in source.split("."):
                                if isinstance(val, dict):
                                    val = val.get(part)
                                else:
                                    val = None
                                    break
                            row[col] = val
                        else:
                            row[col] = item.get(source)
                    else:
                        row[col] = None
                rows.append(row)
    else:
        # Non-participant tables: use generic extraction
        items = _get_from_path(match, path)
        if not items:
            return rows
        for item in items:
            row = {}
            for col, source in fields.items():
                if col == "match_id":
                    row[col] = match_id
                    continue
                if callable(source):
                    try:
                        row[col] = source(item, match)
                    except Exception:
                        row[col] = None
                elif isinstance(source, str):
                    if "." in source:
                        val = item
                        for part in source.split("."):
                            if isinstance(val, dict):
                                val = val.get(part)
                            else:
                                val = None
                                break
                        row[col] = val
                    else:
                        row[col] = item.get(source)
                else:
                    row[col] = None
            rows.append(row)

    return rows


def clean_matches(
    raw_dir: Path,
    out: Path,
    preset: str = "default",
):
    """
    Read raw match JSON files, extract normalized tables,
    apply cleaning preset, and write CSVs.

    Output: one CSV per table.
    """
    if preset not in CLEAN_PRESETS:
        raise ValueError(f"Unknown preset: {preset}")

    preset_cfg = CLEAN_PRESETS[preset]

    tables = {table_name: [] for table_name in CLEAN_SCHEMAS}

    region = None
    for json_file in raw_dir.glob("*.json"):
        with open(json_file, "r") as f:
            match = json.load(f)

        if region is None:
            match_id = match.get("metadata", {}).get("match_id", "")
            if match_id and "_" in match_id:
                region = match_id.split("_")[0]
            else:
                region = "unknown"

        for table_name, schema in CLEAN_SCHEMAS.items():
            extracted_rows = _extract_rows(match, schema)
            tables[table_name].extend(extracted_rows)

    out = out / f"matches_{region}"
    out.mkdir(parents=True, exist_ok=True)

    # ---- apply presets + write csv ----
    for table_name, rows in tables.items():
        if table_name not in preset_cfg:
            continue

        filtered = _filter_columns(rows, preset_cfg[table_name])
        if not filtered:
            continue

        out_path = out / f"{table_name}.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=filtered[0].keys())
            writer.writeheader()
            writer.writerows(filtered)

    return True