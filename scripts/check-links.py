#!/usr/bin/env python3
"""check-links.py - Verify URLs and SAP Note citations in skill files.

Extracts all URLs and SAP Note references from SKILL.md and reference files,
then checks:
  1. URL liveness via HTTP HEAD (with fallback to GET).
  2. SAP Note existence via me.sap.com HEAD check.

Usage:
    python3 scripts/check-links.py [--offline] [--timeout SECONDS] [--workers N]

Options:
    --offline   Skip HTTP checks; only extract and report link inventory.
    --timeout   HTTP request timeout in seconds (default: 20).
    --workers   Max concurrent HTTP workers (default: 5).

Exit codes:
    0  All links OK (or --offline mode).
    1  One or more broken links found.
    2  Script error.
"""

import argparse
import os
import re
import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ──────────────────────────────────────────────
# Extraction
# ──────────────────────────────────────────────

def find_skill_files(repo_root: str) -> list[tuple[str, str]]:
    """Return list of (skill_name, file_path) for all .md files in skills tree."""
    skills_dir = os.path.join(repo_root, ".agents", "skills")
    results = []
    for skill_name in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_dir):
            continue
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if os.path.isfile(skill_file):
            results.append((skill_name, skill_file))
        # Also check reference files
        ref_dir = os.path.join(skill_dir, "references")
        if os.path.isdir(ref_dir):
            for ref_file in sorted(os.listdir(ref_dir)):
                ref_path = os.path.join(ref_dir, ref_file)
                if os.path.isfile(ref_path) and ref_file.endswith(".md"):
                    results.append((f"{skill_name}/references/{ref_file}", ref_path))
    return results


def extract_urls(text: str) -> list[str]:
    """Extract all HTTP(S) URLs from text."""
    urls = re.findall(r'https?://[^\s\)>\]"\'`]+', text)
    # Clean trailing punctuation that isn't part of URLs
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;:!?)")
        # Balance parentheses — URLs in markdown often have trailing )
        open_parens = url.count("(")
        close_parens = url.count(")")
        while close_parens > open_parens and url.endswith(")"):
            url = url[:-1]
            close_parens -= 1
        if url:
            cleaned.append(url)
    return cleaned


def extract_sap_notes(text: str) -> list[str]:
    """Extract all SAP Note numbers from text."""
    return re.findall(r'SAP Note (\d+)', text)


def build_inventory(repo_root: str) -> tuple[dict, dict]:
    """Build URL and SAP Note inventories.

    Returns:
        url_map: {url: [source_file, ...]}
        note_map: {note_number: [source_file, ...]}
    """
    url_map: dict[str, list[str]] = {}
    note_map: dict[str, list[str]] = {}

    for source_name, file_path in find_skill_files(repo_root):
        text = open(file_path, encoding="utf-8").read()

        for url in extract_urls(text):
            url_map.setdefault(url, []).append(source_name)

        for note in extract_sap_notes(text):
            note_map.setdefault(note, []).append(source_name)

    return url_map, note_map


# ──────────────────────────────────────────────
# HTTP checking
# ──────────────────────────────────────────────

def check_url(url: str, timeout: int = 20) -> dict:
    """Check a single URL via HEAD (fallback GET). Returns result dict."""
    import urllib.request
    import urllib.error
    import ssl

    result = {"url": url, "status": None, "redirect": None, "error": None}

    # Create a context that doesn't verify SSL (some SAP sites have cert issues)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {"User-Agent": "Mozilla/5.0 SAP-Skills-Validator/1.0"}

    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                result["status"] = resp.status
                if resp.url != url:
                    result["redirect"] = resp.url
                return result
        except urllib.error.HTTPError as e:
            result["status"] = e.code
            if method == "GET" or e.code not in (405, 403):
                # 405 = Method Not Allowed for HEAD, retry with GET
                # 403 = Forbidden for HEAD, retry with GET
                return result
        except urllib.error.URLError as e:
            result["error"] = str(e.reason)
            return result
        except Exception as e:
            result["error"] = str(e)
            return result

    return result


def check_sap_note(note_number: str, timeout: int = 20) -> dict:
    """Check if a SAP Note exists via me.sap.com."""
    url = f"https://me.sap.com/notes/{note_number}"
    result = check_url(url, timeout=timeout)
    result["note_number"] = note_number
    return result


# ──────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────

def print_inventory(url_map: dict, note_map: dict):
    """Print a summary of the link inventory."""
    print(f"\n{'='*60}")
    print(f"Link Inventory")
    print(f"{'='*60}")
    print(f"  Unique URLs:      {len(url_map)}")
    print(f"  Unique SAP Notes: {len(note_map)}")

    # Domain breakdown
    domains: dict[str, int] = {}
    for url in url_map:
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1
        except Exception:
            pass

    print(f"\n  URL domains:")
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")

    print(f"\n  SAP Notes: {', '.join(sorted(note_map.keys(), key=int))}")


def print_results(url_results: list[dict], note_results: list[dict],
                  url_map: dict, note_map: dict):
    """Print check results as a report."""
    broken_urls = [r for r in url_results if r["status"] is None or r["status"] >= 400]
    redirected_urls = [r for r in url_results if r["redirect"] and r["status"] and r["status"] < 400]
    ok_urls = [r for r in url_results if r["status"] and r["status"] < 400 and not r["redirect"]]

    broken_notes = [r for r in note_results if r["status"] is None or r["status"] >= 400]

    print(f"\n{'='*60}")
    print(f"Link Check Results")
    print(f"{'='*60}")

    # Broken URLs
    if broken_urls:
        print(f"\n## Broken URLs ({len(broken_urls)})")
        print(f"{'Skill':<45} {'Status':<8} URL")
        print(f"{'-'*45} {'-'*8} {'-'*40}")
        for r in sorted(broken_urls, key=lambda x: x["url"]):
            sources = ", ".join(url_map.get(r["url"], ["?"]))
            status = str(r["status"]) if r["status"] else r["error"][:30]
            print(f"{sources[:44]:<45} {status:<8} {r['url']}")

    # Redirected URLs
    if redirected_urls:
        print(f"\n## Redirected URLs ({len(redirected_urls)}) — verify target is correct")
        print(f"{'Skill':<40} Original → Redirect")
        print(f"{'-'*40} {'-'*60}")
        for r in sorted(redirected_urls, key=lambda x: x["url"]):
            sources = ", ".join(url_map.get(r["url"], ["?"]))
            print(f"{sources[:39]:<40} {r['url']}")
            print(f"{'':40} → {r['redirect']}")

    # Broken SAP Notes
    if broken_notes:
        print(f"\n## Broken SAP Notes ({len(broken_notes)})")
        print(f"{'Note':<12} {'Status':<8} Referenced by")
        print(f"{'-'*12} {'-'*8} {'-'*40}")
        for r in sorted(broken_notes, key=lambda x: x["note_number"]):
            sources = ", ".join(note_map.get(r["note_number"], ["?"]))
            status = str(r["status"]) if r["status"] else r["error"][:30]
            print(f"{r['note_number']:<12} {status:<8} {sources}")

    # Summary
    print(f"\n## Summary")
    print(f"  URLs:      {len(ok_urls)} OK, {len(redirected_urls)} redirected, {len(broken_urls)} broken (of {len(url_results)} checked)")
    print(f"  SAP Notes: {len(note_results) - len(broken_notes)} OK, {len(broken_notes)} broken (of {len(note_results)} checked)")

    return len(broken_urls) + len(broken_notes)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Check URLs and SAP Note citations in skill files")
    parser.add_argument("--offline", action="store_true",
                        help="Skip HTTP checks; only extract and report inventory")
    parser.add_argument("--timeout", type=int, default=20,
                        help="HTTP request timeout in seconds (default: 20)")
    parser.add_argument("--workers", type=int, default=5,
                        help="Max concurrent HTTP workers (default: 5)")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    url_map, note_map = build_inventory(repo_root)

    print_inventory(url_map, note_map)

    if args.offline:
        print("\n--offline mode: skipping HTTP checks")
        return 0

    # Check URLs
    print(f"\nChecking {len(url_map)} unique URLs (timeout={args.timeout}s, workers={args.workers})...")
    url_results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_url, url, args.timeout): url for url in url_map}
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            url_results.append(result)
            status = result["status"] or "ERR"
            if result["status"] and result["status"] < 400:
                marker = "."
            else:
                marker = "X"
            if done % 20 == 0 or marker == "X":
                print(f"  [{done}/{len(url_map)}] {marker} {status} {futures[future][:60]}")

    # Check SAP Notes
    print(f"\nChecking {len(note_map)} unique SAP Notes...")
    note_results = []
    for note in sorted(note_map.keys(), key=int):
        result = check_sap_note(note, args.timeout)
        note_results.append(result)
        status = result["status"] or "ERR"
        marker = "." if result["status"] and result["status"] < 400 else "X"
        print(f"  {marker} Note {note}: {status}")
        time.sleep(0.5)  # Rate limit for me.sap.com

    broken_count = print_results(url_results, note_results, url_map, note_map)

    return 1 if broken_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
