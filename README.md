# TFT Info Collector

A lightweight CLI tool for collecting **Teamfight Tactics (TFT)** data from the Riot API, focused on **high-elo match patterns** rather than rigid “meta comps”.

This project is designed for **data analysis and visualization**, not real-time stat tracking.

---

## What this tool does

- Fetch **PUUIDs** from high-elo ladders (Challenger → Grandmaster → Master)
- Fetch **match data** for those players
- Store **raw match JSON** for flexible downstream analysis
- Avoid duplicate matches across players automatically

You can later analyze:
- Early → mid → late game boards
- Item progression
- Augment choices
- Economy and rolling behavior
- Top-4 consistency and play patterns

---

## Important limitations (by design)

- **Match fetching is limited to ONE region per run**
  - Riot match IDs are region-scoped
  - You must run the tool separately for each region (e.g. `na1`, `euw1`)
- Per-player match limits are **recency windows**, not guaranteed quotas
  - Overlapping matches across players are deduplicated automatically

This keeps the dataset clean and avoids artificial inflation.

---

## Installation

```bash
git clone https://github.com/aqingzeo/tft_info_collector
cd tft_info_collector
pip install -e .
```

Create a `.env` file:

```env
RIOT_API_KEY=your_api_key_here
```

---

## Usage

### Fetch player IDs (PUUIDs)

```bash
tft-collector fetch-ids -p na1 -c 200
```

- `-p / --platform` → region platform (default: `na1`)
- `-c / --count` → number of players to collect

---

### Fetch matches

```bash
tft-collector fetch-matches
```

- Uses previously fetched PUUIDs
- Automatically skips duplicate matches
- Saves raw match JSON to `data/raw/`

---

## Data layout

```
data/
├── raw/
│   ├── players.json
│   └── matches/
└── processed/   # adding later
```

---

## License

GNU GPL-3.0


## Disclaimer

This project is **not affiliated with Riot Games**.  
All data is fetched via the official Riot API and used for research and analysis purposes only.
