#!/usr/bin/env python3
"""Fetch GitHub repos and inject project cards into index.html."""

import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GH_USERNAME", "JiamingShi-JsPhys")
TOKEN = os.environ.get("GITHUB_TOKEN")
INDEX = Path("index.html")

EXCLUDED = {
    USERNAME,
    f"{USERNAME}.github.io",
    "profile",
}

MAX_PROJECTS = 6


def fetch_repos():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github+json",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def filter_and_sort(repos):
    out = []
    for r in repos:
        if r.get("fork"):
            continue
        if r.get("archived"):
            continue
        if r["name"] in EXCLUDED:
            continue
        if r["name"].startswith("."):
            continue
        out.append(r)

    # Sort: stars desc, then pushed_at desc (most recent first)
    out.sort(
        key=lambda r: (
            -r.get("stargazers_count", 0),
            r.get("pushed_at", ""),
        ),
        reverse=False,
    )
    # Fix: pushed_at needs descending, so do a second pass for stable ordering
    out.sort(key=lambda r: r.get("pushed_at", ""), reverse=True)
    out.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)

    return out[:MAX_PROJECTS]


def xml_escape(s):
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )


def make_card(r):
    name = xml_escape(r["name"])
    desc = xml_escape((r.get("description") or "").strip())
    url = r["html_url"]

    if len(desc) > 140:
        desc = desc[:137].rstrip() + "..."

    lines = [
        '<div class="project-card">',
        '  <div class="project-title">',
        f'    <a href="{url}">{name}</a>',
        '  </div>',
    ]
    if desc:
        lines.append(f'  <div class="project-desc">{desc}</div>')
    lines.append('</div>')
    return "\n".join(lines)


def inject(html, cards_html):
    pattern = re.compile(
        r"(<!-- PROJECTS_START -->)(.*?)(<!-- PROJECTS_END -->)",
        re.DOTALL,
    )
    if not pattern.search(html):
        raise RuntimeError(
            "Markers not found in index.html. "
            "Please add <!-- PROJECTS_START --> and <!-- PROJECTS_END --> "
            "around the project cards."
        )
    replacement = (
        "<!-- PROJECTS_START -->\n"
        + cards_html
        + "\n<!-- PROJECTS_END -->"
    )
    return pattern.sub(replacement, html)


def main():
    if not INDEX.exists():
        raise FileNotFoundError("index.html not found")

    repos = fetch_repos()
    picked = filter_and_sort(repos)
    print(f"Picked {len(picked)} repos (out of {len(repos)})")
    for r in picked:
        print(f"  - {r['name']} (stars={r.get('stargazers_count', 0)})")

    cards = "\n".join(make_card(r) for r in picked)

    html = INDEX.read_text(encoding="utf-8")
    new_html = inject(html, cards)

    if new_html == html:
        print("No change.")
        return

    INDEX.write_text(new_html, encoding="utf-8")
    print("OK index.html updated")


if __name__ == "__main__":
    main()
