# nanos-world Changelogs Archive

Automated archive and map of all [nanos world](https://nanos-world.com/) game changelogs.

## 🗺️ Changelog Map & Index

Browse the complete historical index of all versions:
👉 **[View Full Changelog Map (CHANGELOG_MAP.md)](./CHANGELOG_MAP.md)**

All individual markdown changelogs are stored in [`changelogs/`](./changelogs/).

---

## 🚀 Running the Fetcher & Generator

The Python script [`fetch_changelogs.py`](./fetch_changelogs.py) batches and downloads all changelogs from the nanos world API (`https://api.nanos-world.com/game/changelog`) with pagination (`limit=100`), formats each release into an individual markdown file in `changelogs/<name>.md`, and updates the map.

### Requirements

- Python 3.8+ (uses standard library only: `urllib`, `json`, `pathlib`, etc. — no external dependencies needed)

### Usage

Run the script directly:

```bash
python3 fetch_changelogs.py
```

### Options

```bash
python3 fetch_changelogs.py --help
```

- `--output-dir`, `-o`: Directory to save individual changelog markdown files (default: `changelogs`)
- `--map-file`, `-m`: Output markdown file for the changelog map index (default: `CHANGELOG_MAP.md`)
- `--limit`, `-l`: Number of changelogs per batch request (default: `100`)
- `--delay`, `-d`: Delay in seconds between batch requests (default: `0.2`)
- `--no-clean`: Do not clean existing files in output directory before writing

---

## 📁 Repository Structure

```
nanos-changelog/
├── CHANGELOG_MAP.md     # Master map/index linking all releases
├── changelogs/          # Individual markdown files per version (e.g. 1.151.3.md)
├── fetch_changelogs.py  # Automation script to fetch and generate files
└── README.md
```
