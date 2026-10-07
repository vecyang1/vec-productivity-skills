#!/usr/bin/env python3
"""opencli_radar.py — Multi-source discovery, pagination, and diagnostic-first audit for OpenCLI plugins.

Provides end-to-end ecosystem discovery across:
1. Local OpenCLI estate (built-in commands & custom adapters in ~/.opencli/clis/)
2. GitHub convention queries (opencli-plugin-*, opencli-adapter-*, high-star repos)
3. Official OpenCLI-Hub registry table (jackwener/OpenCLI-Hub)
4. NPM package registry (opencli-plugin-*)

Usage:
  python3 opencli_radar.py diagnose <site_or_url> [--json]
  python3 opencli_radar.py query <keyword> [--json] [--fresh]
  python3 opencli_radar.py census [--json] [--fresh]
  python3 opencli_radar.py scan [--json] [--fresh]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CACHE_FILE = Path(os.environ.get("OPENCLI_RADAR_CACHE", Path.home() / ".opencli" / "cache" / "ecosystem_radar.json"))

KNOWN_OPEN_SOURCE_LICENSES = {
    "mit", "apache-2.0", "agpl-3.0", "agpl-3.0-or-later", "gpl-3.0", "gpl-3.0-or-later",
    "gpl-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "mpl-2.0", "unlicense", "cc0-1.0"
}

DOMAIN_SITE_MAP = {
    "x.com": "twitter",
    "twitter.com": "twitter",
    "bilibili.com": "bilibili",
    "goofish.com": "xianyu",
    "2.taobao.com": "xianyu",
    "taobao.com": "taobao",
    "github.com": "github",
    "weibo.com": "weibo",
    "juejin.cn": "juejin",
    "douyin.com": "douyin",
    "xiaohongshu.com": "xiaohongshu",
    "xhslink.com": "xiaohongshu",
    "zhihu.com": "zhihu",
    "linkedin.com": "linkedin",
    "clarity.ms": "clarity",
    "claspo.io": "claspo",
    "notion.so": "notion",
    "feishu.cn": "feishu",
    "larksuite.com": "feishu",
}

SITE_ALIAS_MAP = {
    "goofish": "xianyu",
    "xy": "xianyu",
    "xhs": "xiaohongshu",
    "red": "xiaohongshu",
    "x": "twitter",
    "tweet": "twitter",
}

KNOWN_COLLISION_PREFIXES = (
    "xyd-js/openapi2opencli",
    "xyd-js/opencli2go",
    "xyd-js/opencli2rust",
    "xyd-js/opencli-remark",
    "xyd-js/opencli-completion",
    "xyd-js/",
    "openclidev/specification",
)


def is_legitimate_opencli_repo(full_name_or_url: str) -> bool:
    """Filter out unrelated OpenAPI->CLI spec generators and false substring collisions."""
    repo = full_name_or_url.lower()
    for col in KNOWN_COLLISION_PREFIXES:
        if col in repo:
            return False
    for false_positive in ("openclip", "openclicky", "openclimate", "openclimbing", "openclinic", "openclient", "openclide", "openclix"):
        if false_positive in repo and not ("opencli-plugin" in repo or "opencli-adapter" in repo):
            return False
    return "opencli" in repo


def normalize_target_site(query_or_url: str) -> str:
    """Normalize a URL, repository name, or raw site string into a canonical site slug."""
    text = query_or_url.strip()
    if text.startswith("http://") or text.startswith("https://"):
        try:
            parsed = urllib.parse.urlparse(text)
            host = parsed.netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            for domain, slug in DOMAIN_SITE_MAP.items():
                if host == domain or host.endswith("." + domain):
                    return slug
            parts = host.split(".")
            if len(parts) >= 2:
                return parts[-2]
            return host
        except Exception:
            pass

    slug = text.lower()
    for prefix in ("opencli-plugin-", "opencli-adapter-", "opencli-"):
        if slug.startswith(prefix):
            slug = slug[len(prefix):]
            break

    slug = re.sub(r"[^a-z0-9_-]", "-", slug)
    return SITE_ALIAS_MAP.get(slug, slug)


def triage_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Audit candidate repository for license, security, and maintenance status."""
    license_spdx = candidate.get("license_spdx")
    spdx_clean = license_spdx.lower() if isinstance(license_spdx, str) else ""
    has_license = bool(license_spdx and spdx_clean not in ("none", "noassertion"))
    is_open_source = has_license and spdx_clean in KNOWN_OPEN_SOURCE_LICENSES

    stars = candidate.get("stars", 0)
    pushed_at = candidate.get("pushed_at") or candidate.get("updated_at") or ""
    
    # Calculate days since last push
    days_since_push = 999
    if pushed_at:
        try:
            dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_since_push = (datetime.now(timezone.utc) - dt).days
        except Exception:
            pass

    if candidate.get("source") in ("local_builtin", "local_custom"):
        verdict = "REUSE_LOCAL"
        verdict_reason = "Already installed and operational in local OpenCLI estate."
    elif not has_license:
        verdict = "READ_ONLY"
        verdict_reason = "Unlicensed repository (All Rights Reserved). Use as prior art for reverse-engineering only; do not vendor or fork."
    elif not is_open_source:
        verdict = "READ_ONLY"
        verdict_reason = f"Non-standard license '{license_spdx}'. Review legal terms before vendoring."
    elif days_since_push > 365 and stars < 5:
        verdict = "FORK_AND_VENDOR"
        verdict_reason = f"Open-source ({license_spdx}) but unmaintained ({days_since_push} days inactive). Safe to fork and vendor locally to ~/.opencli/clis/."
    else:
        verdict = "INSTALL"
        verdict_reason = f"Active open-source ({license_spdx}) plugin ready for installation."

    return {
        **candidate,
        "has_license": has_license,
        "is_open_source": is_open_source,
        "days_since_push": days_since_push,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
    }


def fetch_local_inventory() -> Dict[str, Dict[str, Any]]:
    """Scan local OpenCLI installed commands and custom adapters."""
    inventory: Dict[str, Dict[str, Any]] = {}
    
    # 1. Probe built-in and user commands via opencli list -f json
    try:
        res = subprocess.run(["opencli", "list", "-f", "json"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            for item in data:
                site = item.get("site")
                if not site:
                    continue
                canonical = normalize_target_site(site)
                if canonical not in inventory:
                    inventory[canonical] = {
                        "site": site,
                        "canonical_site": canonical,
                        "source": "local_builtin",
                        "commands": [],
                        "description": item.get("description", ""),
                    }
                cmd_name = item.get("name")
                if cmd_name and cmd_name not in inventory[canonical]["commands"]:
                    inventory[canonical]["commands"].append(cmd_name)
    except Exception:
        pass

    # 2. Probe ~/.opencli/clis/
    custom_dir = Path.home() / ".opencli" / "clis"
    if custom_dir.is_dir():
        for sub in custom_dir.iterdir():
            if sub.is_dir() and not sub.name.startswith((".", "_")):
                canonical = normalize_target_site(sub.name)
                commands = [f.stem for f in sub.glob("*.js") if not f.name.startswith((".", "_"))]
                if canonical not in inventory or inventory[canonical]["source"] != "local_custom":
                    inventory[canonical] = {
                        "site": sub.name,
                        "canonical_site": canonical,
                        "source": "local_custom",
                        "commands": commands,
                        "path": str(sub),
                        "description": f"Local custom adapter in ~/.opencli/clis/{sub.name}",
                    }

    return inventory


def fetch_github_repositories(query: str, max_items: int = 200) -> Tuple[List[Dict[str, Any]], int, bool]:
    """Fetch GitHub repositories with strict pagination handling and completeness tracking."""
    items: List[Dict[str, Any]] = []
    total_count = 0
    page = 1
    per_page = 100

    while len(items) < max_items:
        cmd = [
            "gh", "api", "-X", "GET",
            f"search/repositories?q={urllib.parse.quote(query)}&per_page={per_page}&page={page}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            break
        try:
            data = json.loads(res.stdout)
            total_count = data.get("total_count", 0)
            page_items = data.get("items", [])
            if not page_items:
                break
            for item in page_items:
                full_name = item.get("full_name", "")
                if is_legitimate_opencli_repo(full_name):
                    license_obj = item.get("license") or {}
                    items.append({
                        "name": item.get("name", ""),
                        "full_name": full_name,
                        "repo_url": item.get("html_url", ""),
                        "description": item.get("description") or "",
                        "stars": item.get("stargazers_count", 0),
                        "pushed_at": item.get("pushed_at", ""),
                        "license_spdx": license_obj.get("spdx_id"),
                        "source": "github_convention",
                        "canonical_site": normalize_target_site(item.get("name", "")),
                    })
            if len(items) >= total_count or len(page_items) < per_page:
                break
            page += 1
        except Exception:
            break

    is_complete = (len(items) >= total_count) or (total_count == 0)
    return items, total_count, is_complete


def fetch_official_hub_plugins() -> List[Dict[str, Any]]:
    """Fetch official registry table from jackwener/OpenCLI-Hub."""
    hub_plugins = []
    cmd = ["gh", "api", "repos/jackwener/OpenCLI-Hub/readme", "--jq", ".content"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        import base64
        try:
            readme_text = base64.b64decode(res.stdout.strip()).decode("utf-8", errors="ignore")
            for line in readme_text.splitlines():
                if line.startswith("|") and "github.com" in line and not line.startswith("| Plugin"):
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cols) >= 2:
                        match = re.search(r"\[(.*?)\]\((https://github\.com/.*?)\)", cols[0])
                        if match:
                            name, url = match.groups()
                            desc = cols[1] if len(cols) > 1 else ""
                            hub_plugins.append({
                                "name": name,
                                "repo_url": url,
                                "description": desc,
                                "source": "official_hub",
                                "canonical_site": normalize_target_site(name),
                            })
        except Exception:
            pass
    return hub_plugins


def fetch_npm_plugins() -> List[Dict[str, Any]]:
    """Query npm registry search API for opencli packages."""
    npm_plugins = []
    try:
        cmd = ["curl", "-s", "https://registry.npmjs.org/-/v1/search?text=opencli-plugin&size=50"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            for obj in data.get("objects", []):
                pkg = obj.get("package", {})
                name = pkg.get("name", "")
                if is_legitimate_opencli_repo(name) and ("opencli-plugin" in name or "opencli-adapter" in name):
                    npm_plugins.append({
                        "name": name,
                        "repo_url": pkg.get("links", {}).get("npm") or f"https://www.npmjs.com/package/{name}",
                        "description": pkg.get("description", ""),
                        "source": "npm_registry",
                        "canonical_site": normalize_target_site(name),
                        "updated_at": pkg.get("date", ""),
                    })
    except Exception:
        pass
    return npm_plugins


def run_full_census(use_cache: bool = True) -> Dict[str, Any]:
    """Execute multi-layer census with caching, complete pagination, and deduplication."""
    if use_cache and CACHE_FILE.is_file():
        try:
            mtime = CACHE_FILE.stat().st_mtime
            if time.time() - mtime < 3600:  # 1 hour TTL
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

    # 1. Fetch GitHub convention queries
    gh_plugins, gh_plugin_total, gh_plugin_complete = fetch_github_repositories("opencli-plugin in:name")
    gh_adapters, gh_adapter_total, gh_adapter_complete = fetch_github_repositories("opencli-adapter in:name")
    gh_high_stars, _, _ = fetch_github_repositories("opencli in:name sort:stars", max_items=100)
    
    # Merge and deduplicate GitHub repos
    gh_merged: Dict[str, Dict[str, Any]] = {}
    for r in gh_plugins + gh_adapters + gh_high_stars:
        url = r.get("repo_url")
        if url and url not in gh_merged:
            gh_merged[url] = r

    # 2. Fetch Official Hub plugins
    hub_plugins = fetch_official_hub_plugins()

    # 3. Fetch NPM plugins
    npm_plugins = fetch_npm_plugins()

    # 4. Triaged community candidates
    triaged_community = [triage_candidate(c) for c in gh_merged.values()]

    # 5. Local inventory
    local_inv = fetch_local_inventory()

    # Statistics
    total_community = len(triaged_community)
    licensed_count = sum(1 for c in triaged_community if c.get("has_license"))
    license_rate = round((licensed_count / total_community * 100), 1) if total_community else 0.0
    zero_star_count = sum(1 for c in triaged_community if c.get("stars", 0) == 0)
    zero_star_rate = round((zero_star_count / total_community * 100), 1) if total_community else 0.0

    census = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "github_plugins_total_api": gh_plugin_total,
            "github_adapters_total_api": gh_adapter_total,
            "community_repos_ingested": total_community,
            "official_hub_listed": len(hub_plugins),
            "hub_capture_rate_percent": round((len(hub_plugins) / total_community * 100), 1) if total_community else 0.0,
            "npm_packages_found": len(npm_plugins),
            "local_estate_sites": len(local_inv),
            "licensed_repos_count": licensed_count,
            "license_rate_percent": license_rate,
            "zero_star_count": zero_star_count,
            "zero_star_percent": zero_star_rate,
            "pagination_verified": gh_plugin_complete and gh_adapter_complete,
        },
        "community_plugins": triaged_community,
        "official_hub": hub_plugins,
        "npm_packages": npm_plugins,
        "local_inventory": local_inv,
    }

    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(census, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return census


def diagnose_site(
    query_or_url: str,
    local_inventory: Optional[Dict[str, Any]] = None,
    community_inventory: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Diagnostic-first verification for a site: explains match source, license, and actionable command."""
    canonical_site = normalize_target_site(query_or_url)
    
    if local_inventory is None:
        local_inventory = fetch_local_inventory()
    if community_inventory is None:
        census = run_full_census(use_cache=True)
        community_inventory = census.get("community_plugins", [])

    matched_local = local_inventory.get(canonical_site)
    matched_community = [
        c for c in community_inventory
        if c.get("canonical_site") == canonical_site or canonical_site in c.get("name", "").lower()
    ]

    # Rank community matches by stars and recency
    matched_community.sort(key=lambda x: (x.get("stars", 0), x.get("pushed_at", "")), reverse=True)

    # Determine verdict and actionable command
    if matched_local:
        verdict = "REUSE_LOCAL"
        source = matched_local.get("source", "local")
        cmds = matched_local.get("commands", [])
        example_cmd = f"opencli {canonical_site} {cmds[0]}" if cmds else f"opencli {canonical_site} --help"
        reason = f"Site is already supported locally via {source} ({len(cmds)} commands available)."
        actionable_command = example_cmd
    elif matched_community:
        best = matched_community[0]
        verdict = best.get("verdict", "INSTALL")
        reason = best.get("verdict_reason", "")
        repo_url = best.get("repo_url", "")
        clean_repo = repo_url.replace("https://github.com/", "")
        if verdict == "INSTALL":
            actionable_command = f"opencli plugin install github:{clean_repo}"
        elif verdict == "FORK_AND_VENDOR":
            actionable_command = f"git clone {repo_url} ~/.opencli/clis/{canonical_site}"
        else:  # READ_ONLY
            actionable_command = f"opencli browser init {canonical_site}/<command> # (inspect {repo_url} as prior art only)"
    else:
        verdict = "BUILD_NEW"
        reason = f"No existing adapter or community plugin found for '{canonical_site}'. Ready to scaffold."
        actionable_command = f"opencli browser init {canonical_site}/<command>"

    return {
        "query": query_or_url,
        "canonical_site": canonical_site,
        "verdict": verdict,
        "verdict_reason": reason,
        "actionable_command": actionable_command,
        "matched_local": matched_local,
        "matched_community": matched_community,
    }


def format_diagnosis_report(diag: Dict[str, Any]) -> str:
    """Format human-readable diagnostic report."""
    lines = [
        "=" * 68,
        f"🎯 OPENCLI RADAR DIAGNOSTIC REPORT: {diag['canonical_site'].upper()}",
        "=" * 68,
        f"• Input Query:        {diag['query']}",
        f"• Canonical Slug:     {diag['canonical_site']}",
        f"• Recommended Verdict:{diag['verdict']}",
        f"• Verdict Rationale:  {diag['verdict_reason']}",
        f"• Actionable Command: {diag['actionable_command']}",
        "-" * 68,
    ]

    loc = diag.get("matched_local")
    if loc:
        lines.append(f"[LAYER 1: LOCAL ESTATE HIT] ({loc.get('source', 'local')})")
        lines.append(f"  Commands: {', '.join(loc.get('commands', [])) or 'default'}")
        lines.append(f"  Path:     {loc.get('path', 'built-in')}")
    else:
        lines.append("[LAYER 1: LOCAL ESTATE] Not installed.")

    comm = diag.get("matched_community", [])
    if comm:
        lines.append(f"\n[LAYER 2 & 3: COMMUNITY HITS] ({len(comm)} candidates found)")
        for idx, c in enumerate(comm[:3], 1):
            lic = c.get('license_spdx') or 'All Rights Reserved'
            lines.append(f"  {idx}. {c.get('name')} (★{c.get('stars', 0)}) — License: {lic}")
            lines.append(f"     URL: {c.get('repo_url')}")
            lines.append(f"     Verdict: {c.get('verdict')} ({c.get('verdict_reason')})")
    else:
        lines.append("\n[LAYER 2 & 3: COMMUNITY] No community plugins found.")

    lines.append("\n[SECURITY BOUNDARY REMINDER]")
    lines.append("  • OpenCLI plugins execute in-process with access to all active Chrome sessions.")
    lines.append("  • Install time: `--ignore-scripts` blocks malicious lifecycle scripts.")
    lines.append("  • Run time: Always audit network egress (`rg 'fetch|axios'`) before execution.")
    lines.append("=" * 68)
    return "\n".join(lines)


def format_census_report(census: Dict[str, Any]) -> str:
    """Format human-readable census statistical report."""
    s = census.get("summary", {})
    lines = [
        "=" * 68,
        "📊 OPENCLI COMMUNITY ECOSYSTEM LIVE CENSUS",
        "=" * 68,
        f"• Timestamp:                     {census.get('timestamp')}",
        f"• GitHub Plugins API Count:       {s.get('github_plugins_total_api')} repos",
        f"• GitHub Adapters API Count:      {s.get('github_adapters_total_api')} repos",
        f"• Community Repos Ingested:       {s.get('community_repos_ingested')} unique repos",
        f"• Official Hub Table Count:       {s.get('official_hub_listed')} listed",
        f"• Hub Capture Rate:              {s.get('hub_capture_rate_percent')}% (Official is a floor, not census!)",
        f"• NPM Packages Found:            {s.get('npm_packages_found')} packages",
        f"• Local Machine Supported Sites:  {s.get('local_estate_sites')} sites",
        "-" * 68,
        f"• Open-Source Licensed Repos:     {s.get('licensed_repos_count')} / {s.get('community_repos_ingested')} ({s.get('license_rate_percent')}%)",
        f"• Unlicensed (All Rights Reserved): {s.get('community_repos_ingested', 0) - s.get('licensed_repos_count', 0)} ({round(100.0 - s.get('license_rate_percent', 0), 1)}%)",
        f"• Zero-Star Repos:               {s.get('zero_star_count')} / {s.get('community_repos_ingested')} ({s.get('zero_star_percent')}%)",
        f"• Pagination Full Verification:  {'PASSED (All pages ingested)' if s.get('pagination_verified') else 'PARTIAL'}",
        "=" * 68,
    ]
    return "\n".join(lines)


def main() -> None:
    raw_args = sys.argv[1:]
    # If first argument is an action, default host to 'opencli'
    if raw_args and raw_args[0] in ("diagnose", "query", "census", "scan"):
        raw_args.insert(0, "opencli")

    parser = argparse.ArgumentParser(description="OpenCLI Ecosystem Radar & Diagnostic Engine")
    parser.add_argument("host", nargs="?", default="opencli", help="Host platform (default: opencli)")
    parser.add_argument("command", nargs="?", default="census", choices=["diagnose", "query", "census", "scan"], help="Action")
    parser.add_argument("target", nargs="?", default="", help="Site name, query keyword, or URL")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--fresh", action="store_true", help="Bypass cache and perform live GitHub/npm crawl")

    args = parser.parse_args(raw_args)
    action = args.command
    target = args.target

    if action == "diagnose":
        if not target:
            print("Error: 'diagnose' requires a target site or URL. e.g. opencli-radar diagnose twitter", file=sys.stderr)
            sys.exit(1)
        diag = diagnose_site(target)
        if args.json:
            print(json.dumps(diag, indent=2, ensure_ascii=False))
        else:
            print(format_diagnosis_report(diag))

    elif action in ("census", "scan"):
        census = run_full_census(use_cache=not args.fresh)
        if args.json:
            print(json.dumps(census, indent=2, ensure_ascii=False))
        else:
            print(format_census_report(census))

    elif action == "query":
        census = run_full_census(use_cache=not args.fresh)
        target_clean = target.lower()
        matches = [
            c for c in census.get("community_plugins", [])
            if target_clean in c.get("name", "").lower() or target_clean in c.get("description", "").lower() or target_clean in c.get("canonical_site", "")
        ]
        if args.json:
            print(json.dumps(matches, indent=2, ensure_ascii=False))
        else:
            print(f"\nFound {len(matches)} community plugin matches for '{target}':\n")
            for m in matches:
                print(f"• {m['name']} (★{m.get('stars', 0)}) [{m.get('verdict')}]")
                print(f"  URL: {m['repo_url']}")
                print(f"  License: {m.get('license_spdx') or 'All Rights Reserved'}")
                print(f"  Desc: {m.get('description')}\n")


if __name__ == "__main__":
    main()
