# TFT Info Collector

A lightweight CLI tool for collecting **Teamfight Tactics (TFT)** data from the Riot API, designed for **data analysis and pattern discovery**, not real-time meta chasing.

This project focuses on **how high‑elo players actually play games**, rather than prescribing rigid “best comps”.

---

## What this tool is for

This tool helps you build datasets to analyze:

- Item and unit patterns across top players
- Endgame boards vs early item signals
- Augment usage trends
- Top‑4 consistency and playstyle differences
- Match‑level and participant‑level behaviors

It is intended for:
- data analysis
- visualization
- research
- personal tooling

Not for:
- live stat tracking
- tier lists
- matchmaking overlays

---

## What it does

- Fetches **PUUIDs** from high‑elo ladders  
  (Challenger → Grandmaster → Master)
- Fetches **TFT match data** for those players
- Stores **raw match JSON** for maximum flexibility
- Cleans raw data into **analysis‑ready CSVs**
- Automatically **deduplicates matches**
- Can safely resume after interruptions (rate limits, crashes)

---

## Important design constraints (intentional)

- **One region per run**
  - TFT match IDs are region‑scoped
  - Run the tool separately per region (e.g. `na1`, `euw1`)
- **Match limits are per player, not guaranteed totals**
  - Overlapping matches across players are deduplicated
  - Fewer matches than expected is normal and correct
- Focus is on **patterns**, not volume inflation

---

## Installation

```bash
git clone https://github.com/aqingzeo/tft_info_collector
cd tft_info_collector
pip install -e .
```

Create a `.env` file:

```env
RIOT_API_KEY=your_riot_api_key_here
```

---

## Usage

### Fetch high‑elo player IDs

```bash
tft-collector fetch-ids -p na1 -c 200
```

- `-p / --platform` → region platform (default: `na1`)
- `-c / --count` → number of players to collect

Players are fetched from:
1. Challenger
2. Grandmaster
3. Master  
until the requested count is reached.

---

### Fetch match data

```bash
tft-collector fetch-matches
```

- Uses previously saved PUUIDs
- Automatically skips already fetched players and matches
- Respects Riot API rate limits
- Can be safely re‑run to continue progress

---

### Clean match data into CSV

```bash
tft-collector clean
```

- Converts raw match JSON into analysis‑ready CSVs
- Uses predefined cleaning presets (e.g. `default`)
- Outputs files under `data/clean/`

---

## Data layout

```
data/
├── raw/
│   ├── players.json
│   └── matches/
│       └── NA1_*.json
└── clean/
    └── matches_NA1.csv
```

Raw data is preserved so you can re‑clean with different schemas later.

---

## Versioning philosophy

- `1.0.0` = stable data pipeline + usable CLI
- Future versions may:
  - add new cleaning presets
  - add new derived metrics
  - refine schemas
- Breaking changes will increment the **major version**

---

## License

GNU GPL‑3.0

Commercial reuse by third‑party services is restricted.  
Personal research, forks, and learning use are encouraged.

---

## Disclaimer

This project is **not affiliated with Riot Games**.

All data is accessed via the official Riot API and used strictly for
research and analysis purposes.
