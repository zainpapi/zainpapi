#!/usr/bin/env python3
"""Regenerate the 'My Projects' section of README.md from the GitHub API.

Only touches the content between the PROJECTS:START / PROJECTS:END markers.
Aborts (without modifying anything) if the markers are missing.
"""
import json
import os
import urllib.request

token = os.environ["GITHUB_TOKEN"]
owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")


def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "profile-updater",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


repos = api(f"/users/{owner}/repos?sort=pushed&per_page=15&type=owner")
repos = [r for r in repos if not r["archived"] and r["name"] != repo]

lines = []
for r in repos:
    desc = (r.get("description") or "").strip()
    lang = r.get("language") or "n/a"
    entry = f"- [**{r['name']}**]({r['html_url']})"
    if desc:
        entry += f" — {desc}"
    if lang and lang != "n/a":
        entry += f" ({lang})"
    lines.append(entry)

block = "\r\n".join(lines)

with open("README.md", encoding="utf-8", newline="") as f:
    readme = f.read()

start = "<!-- PROJECTS:START -->"
end = "<!-- PROJECTS:END -->"
if start not in readme or end not in readme:
    print("Markers not found; aborting without modification.")
    raise SystemExit(0)

before = readme.split(start)[0]
after = readme.split(end)[1]
new_readme = before + start + "\r\n" + block + "\r\n" + end + after

with open("README.md", "w", encoding="utf-8", newline="") as f:
    f.write(new_readme)

print(f"Updated projects section with {len(lines)} repos")
