#!/usr/bin/env python3
"""
Nanos World Changelog Fetcher & Generator

Fetches all changelogs from the nanos world API (https://api.nanos-world.com/game/changelog)
using pagination (limit=100 per page), saves each changelog into a separate nicely formatted
markdown file in `changelogs/<name>.md`, and generates a comprehensive `CHANGELOG_MAP.md`.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

API_BASE_URL = "https://api.nanos-world.com/game/changelog"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) "
    "Gecko/20100101 Firefox/153.0"
)


def parse_iso_datetime(date_str: Optional[str]) -> Optional[datetime.datetime]:
    """Parse ISO datetime string into UTC datetime object."""
    if not date_str:
        return None
    try:
        clean_str = date_str.replace("Z", "+00:00")
        return datetime.datetime.fromisoformat(clean_str)
    except Exception:
        return None


def format_release_date(date_str: Optional[str]) -> str:
    """Format release date into human-readable UTC string."""
    dt = parse_iso_datetime(date_str)
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return date_str or "Unknown Date"


def sanitize_filename(name: str) -> str:
    """Sanitize version name to be safe for filenames."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return sanitized or "unknown_version"


def fetch_page(
    page: int,
    limit: int = 100,
    user_agent: str = DEFAULT_USER_AGENT,
    max_retries: int = 3,
    backoff_factor: float = 1.5,
) -> List[Dict[str, Any]]:
    """Fetch a single page of changelogs with retry logic."""
    url = f"{API_BASE_URL}?page={page}&limit={limit}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    raise urllib.error.HTTPError(
                        url, resp.status, f"HTTP status {resp.status}", resp.headers, None
                    )
                raw_data = resp.read().decode("utf-8")
                data = json.loads(raw_data)
                payload = data.get("payload", [])
                if not isinstance(payload, list):
                    print(f"Warning: Expected payload list on page {page}, got {type(payload)}", file=sys.stderr)
                    return []
                return payload
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            if attempt == max_retries:
                print(f"Error fetching page {page} after {max_retries} attempts: {e}", file=sys.stderr)
                raise
            sleep_time = backoff_factor ** attempt
            print(f"Fetch failed for page {page} ({e}). Retrying in {sleep_time:.1f}s... (Attempt {attempt}/{max_retries})")
            time.sleep(sleep_time)

    return []


def fetch_all_changelogs(
    limit: int = 100,
    delay: float = 0.2,
    user_agent: str = DEFAULT_USER_AGENT,
) -> List[Dict[str, Any]]:
    """
    Fetch all changelogs batch by batch using 1-indexed pagination.
    Deduplicates entries while preserving original chronological order.
    """
    all_changelogs: List[Dict[str, Any]] = []
    seen_names: Set[str] = set()
    page = 1

    print(f"📡 Fetching changelogs from {API_BASE_URL} (batch size: {limit})...")

    while True:
        items = fetch_page(page=page, limit=limit, user_agent=user_agent)
        if not items:
            print(f"  Page {page}: 0 items. Finished fetching.")
            break

        new_items_count = 0
        for item in items:
            name = item.get("name")
            if name and name not in seen_names:
                seen_names.add(name)
                all_changelogs.append(item)
                new_items_count += 1

        print(f"  Page {page:2d}: {len(items):3d} items retrieved ({new_items_count:3d} new, total unique: {len(all_changelogs):4d})")

        # If page returned fewer items than limit or no new items, we are done
        if len(items) < limit or new_items_count == 0:
            print("  Reached the end of changelog list.")
            break

        page += 1
        if delay > 0:
            time.sleep(delay)

    print(f"✨ Successfully collected {len(all_changelogs)} unique changelogs.\n")
    return all_changelogs


def format_single_changelog(item: Dict[str, Any]) -> str:
    """Format a single changelog into a clean Markdown document."""
    name = item.get("name", "Unknown")
    released_at = item.get("releasedAt")
    formatted_date = format_release_date(released_at)

    raw_description = item.get("description", "").strip()
    # Normalize line endings
    description = raw_description.replace("\r\n", "\n").replace("\r", "\n")

    lines = [
        f"# nanos world - Version {name}",
        "",
        f"- **Release Date:** {formatted_date}",
        f"- **Raw Timestamp:** `{released_at or 'N/A'}`",
        "",
        "---",
        "",
        description if description else "*No description provided for this release.*",
        "",
    ]

    return "\n".join(lines)


def write_changelog_files(
    changelogs: List[Dict[str, Any]],
    output_dir: Path,
    clean_dir: bool = True,
) -> List[Path]:
    """Write individual formatted changelog files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if clean_dir:
        for existing_file in output_dir.glob("*.md"):
            try:
                existing_file.unlink()
            except OSError as e:
                print(f"Warning: Failed to remove {existing_file}: {e}", file=sys.stderr)

    written_files: List[Path] = []
    for item in changelogs:
        version_name = item.get("name", "unknown")
        filename = f"{sanitize_filename(version_name)}.md"
        filepath = output_dir / filename

        content = format_single_changelog(item)
        filepath.write_text(content, encoding="utf-8")
        written_files.append(filepath)

    print(f"💾 Wrote {len(written_files)} changelog markdown files to `{output_dir}/`.")
    return written_files


CATEGORY_KEYWORDS = {
    "new features", "improvements", "bug fixes", "hotfix", "hotfixes", "hot fix",
    "breaking changes", "changes", "fixes", "general", "features", "additions",
    "scripting", "client", "server", "website", "store", "vault", "docs", "core",
    "account, store & website", "account, store and website", "experimental",
    "hotfix/new features", "hotfix / new features", "known issues", "le incredible and big update"
}


def is_category_header(line: str) -> bool:
    """Check if a line is a section heading or category label."""
    s = line.strip()
    if not s or s.startswith("#"):
        return True

    # Strip emojis, markdown formatting, symbols
    clean = re.sub(r"[^\w\s/&,+-]", "", s).strip()
    clean_lower = clean.lower()

    if clean_lower in CATEGORY_KEYWORDS:
        return True
    if clean_lower.rstrip(":") in CATEGORY_KEYWORDS:
        return True
    if clean_lower.endswith("fixes") or clean_lower.endswith("improvements") or clean_lower.endswith("features"):
        if len(clean_lower.split()) <= 4:
            return True

    return False


def clean_markdown_for_summary(text: str) -> str:
    """Clean markdown artifacts from text for a single-line summary."""
    # Convert [Text](url) -> Text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove markdown formatting (bold, italic, code backticks, strikethrough)
    text = re.sub(r"[*_`~]", "", text)
    # Remove leading list bullets / numbers
    text = re.sub(r"^\s*[-*+]\s+", "", text)
    text = re.sub(r"^\s*\d+[\.\)]\s+", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_summary_snippet(description: str, max_chars: int = 120) -> str:
    """Extract a meaningful single-line summary, filtering out category headings."""
    lines = description.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in lines:
        raw_line = line.strip()
        if not raw_line or is_category_header(raw_line):
            continue

        cleaned = clean_markdown_for_summary(raw_line)
        if cleaned and not is_category_header(cleaned) and len(cleaned) >= 3:
            if len(cleaned) > max_chars:
                return cleaned[:max_chars].rstrip() + "..."
            return cleaned

    # Fallback to first non-empty cleaned line if all looked like headers
    for line in lines:
        cleaned = clean_markdown_for_summary(line)
        if cleaned:
            if len(cleaned) > max_chars:
                return cleaned[:max_chars].rstrip() + "..."
            return cleaned

    return "Update release"


def generate_changelog_map(
    changelogs: List[Dict[str, Any]],
    output_map_path: Path,
    changelogs_rel_dir: str = "changelogs",
) -> None:
    """Generate a comprehensive map / index markdown file of all changelogs."""
    total_count = len(changelogs)
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    latest_version = changelogs[0].get("name", "N/A") if changelogs else "N/A"
    oldest_version = changelogs[-1].get("name", "N/A") if changelogs else "N/A"

    # Group by major.minor prefix (e.g., "1.151", "1.150", "0.5")
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in changelogs:
        name = str(item.get("name", ""))
        parts = name.split(".")
        if len(parts) >= 2:
            group_key = f"v{parts[0]}.{parts[1]}"
        elif len(parts) == 1 and parts[0]:
            group_key = f"v{parts[0]}"
        else:
            group_key = "Other"

        grouped.setdefault(group_key, []).append(item)

    lines: List[str] = [
        "# 🗺️ nanos world - Changelog Map & Index",
        "",
        "> Complete historical index of all nanos world game changelogs.",
        "",
        "## 📊 Summary Statistics",
        "",
        f"- **Total Versions:** {total_count}",
        f"- **Latest Release:** [{latest_version}]({changelogs_rel_dir}/{sanitize_filename(latest_version)}.md)",
        f"- **Earliest Release:** [{oldest_version}]({changelogs_rel_dir}/{sanitize_filename(oldest_version)}.md)",
        f"- **Last Updated:** {now_utc}",
        "",
        "---",
        "",
        "## 📚 Version Series Navigation",
        "",
    ]

    # Quick Jump Links
    jump_links = [f"[`{group}`](#{group.lower().replace('.', '')})" for group in grouped.keys()]
    lines.append(" | ".join(jump_links))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section for each series
    for group, items in grouped.items():
        lines.append(f"### {group}")
        lines.append("")
        lines.append("| Version | Release Date | Key Highlights / Summary |")
        lines.append("| :--- | :--- | :--- |")

        for item in items:
            name = item.get("name", "unknown")
            released_at = item.get("releasedAt")
            dt = parse_iso_datetime(released_at)
            date_display = dt.strftime("%Y-%m-%d") if dt else (released_at or "N/A")
            filename = f"{sanitize_filename(name)}.md"
            link = f"[{name}]({changelogs_rel_dir}/{filename})"
            snippet = extract_summary_snippet(item.get("description", ""))
            # Escape pipe chars for markdown table syntax
            snippet = snippet.replace("|", "\\|")
            lines.append(f"| **{link}** | `{date_display}` | {snippet} |")

        lines.append("")

    output_map_path.parent.mkdir(parents=True, exist_ok=True)
    output_map_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"🗺️  Generated changelog map at `{output_map_path}`.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch all nanos world game changelogs, write individual markdown files, and generate a map."
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("changelogs"),
        help="Directory to save individual changelog markdown files (default: changelogs)",
    )
    parser.add_argument(
        "--map-file",
        "-m",
        type=Path,
        default=Path("CHANGELOG_MAP.md"),
        help="Output markdown file for the changelog map index (default: CHANGELOG_MAP.md)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=100,
        help="Number of changelogs per batch request (default: 100)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=0.2,
        help="Delay in seconds between page requests (default: 0.2)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete existing .md files in output directory before writing",
    )

    args = parser.parse_args()

    changelogs = fetch_all_changelogs(limit=args.limit, delay=args.delay)
    if not changelogs:
        print("No changelogs retrieved. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Write files
    write_changelog_files(changelogs, args.output_dir, clean_dir=not args.no_clean)

    # Compute relative path for links from map file to changelogs directory
    try:
        rel_dir = os.path.relpath(args.output_dir, args.map_file.parent)
    except ValueError:
        rel_dir = str(args.output_dir)

    # Generate Map
    generate_changelog_map(changelogs, args.map_file, changelogs_rel_dir=rel_dir)
    print("\n✅ All changelogs successfully fetched and indexed!")


if __name__ == "__main__":
    main()
