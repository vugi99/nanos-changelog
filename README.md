# 🎮 nanos world - Changelog Archive

[![Total Changelogs](https://img.shields.io/badge/Changelogs-400%2B-blue.svg)](CHANGELOG_MAP.md)
[![Sync Changelogs](https://github.com/vugi99/nanos-changelog/actions/workflows/update-changelogs.yml/badge.svg)](https://github.com/vugi99/nanos-changelog/actions/workflows/update-changelogs.yml)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg?logo=python&logoColor=white)](fetch_changelogs.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated, standalone repository dedicated to archiving, formatting, and indexing all official game changelogs for [**nanos world**](https://nanos-world.com/).

---

## 🗺️ Master Changelog Map & Index

Browse the complete historical release index and jump directly to any version:

👉 **[Open CHANGELOG_MAP.md](./CHANGELOG_MAP.md)** 👈

All individual release notes are stored in the [`changelogs/`](./changelogs/) directory (named by version, e.g. `1.151.3.md`).

---

## ✨ Features

- **Complete History:** Contains all releases from early alpha (`v0.2.0`) to the latest updates.
- **Individual Markdown Files:** One neatly formatted `.md` file per release inside [`changelogs/`](./changelogs/) with clean timestamps and headers.
- **Interactive Index Map:** [`CHANGELOG_MAP.md`](./CHANGELOG_MAP.md) organizes all versions by major/minor series (`v1.151`, `v1.150`, ..., `v0.2`) with release dates and key highlights.
- **Zero-Dependency Automation:** Includes [`fetch_changelogs.py`](./fetch_changelogs.py) which pulls directly from the nanos world API using standard Python libraries.

---

## 🚀 Running the Fetcher & Generator

You can run or re-run the Python script at any time to pull newly released changelogs and update the entire archive and map.

### Requirements

- **Python 3.8+** (Standard library only — no `pip install` or external packages required).

### Sync Changelogs

```bash
python3 fetch_changelogs.py
```

### Command Line Options

```text
usage: fetch_changelogs.py [-h] [--output-dir OUTPUT_DIR] [--map-file MAP_FILE]
                           [--limit LIMIT] [--delay DELAY] [--no-clean]

Fetch all nanos world game changelogs, write individual markdown files, and generate a map.

options:
  -h, --help            show this help message and exit
  --output-dir, -o      Directory to save individual changelog markdown files (default: changelogs)
  --map-file, -m        Output markdown file for the changelog map index (default: CHANGELOG_MAP.md)
  --limit, -l           Number of changelogs per batch request (default: 100)
  --delay, -d           Delay in seconds between page requests (default: 0.2)
  --no-clean            Do not delete existing .md files in output directory before writing
```

---

## 🤖 Automated GitHub Actions Workflow

This repository includes a scheduled GitHub Action workflow ([`update-changelogs.yml`](.github/workflows/update-changelogs.yml)) that keeps the archive always up to date:

- **Schedule:** Runs automatically **every 2 days at 06:00 UTC** (`0 6 */2 * *`).
- **Manual Trigger:** Can be manually triggered at any time from the [GitHub Actions tab](https://github.com/vugi99/nanos-changelog/actions/workflows/update-changelogs.yml) via the **"Run workflow"** button.
- **Auto Commit & Push:** When new game releases are detected from the API, the action automatically commits and pushes the new changelog files and updated index map.

---

## 📁 Repository Structure

```text
nanos-changelog/
├── .gitignore
├── CHANGELOG_MAP.md       # Master index linking every changelog by series
├── changelogs/            # Individual changelog files (e.g. 1.151.3.md, 0.2.0.md)
│   ├── 1.151.3.md
│   ├── 1.151.2.md
│   └── ...
├── fetch_changelogs.py    # Automation script to fetch and generate archive
├── LICENSE                # MIT License
└── README.md              # Repository documentation
```

---

## 🌐 API Source

Data is fetched from the official nanos world API endpoint:

- **Endpoint:** `https://api.nanos-world.com/game/changelog?page={page}&limit={limit}`
- **Documentation:** [docs.nanos-world.com](https://docs.nanos-world.com/)

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
