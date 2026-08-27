---
name: opensky-network-cli
description: Real-time global aircraft radar telemetry, ADS-B position tracking, flight records, and trajectory waypoints via OpenSky Network REST API with 1Password OAuth2 credential resolver and quota ledger.
---

# OpenSky Network CLI (`opensky-network-cli`)

A unified, production-grade CLI and Python SDK for querying real-time flight radar telemetry, active airspace state vectors, historical airport arrivals/departures, and aircraft trajectory tracks via the non-profit OpenSky Network.

## Skill Metadata

- **Origin:** `local`
- **Source:** `~/.gemini/antigravity/skills/opensky-network-cli`
- **Author:** V
- **Created:** 2026-08-27
- **Updated:** 2026-08-27
- **Review status:** `reviewed`

## Quick Commands

```bash
# Navigate to skill directory
cd ~/.gemini/antigravity/skills/opensky-network-cli

# 1. Health & Quota Check (inspect credentials, token & remaining credits)
python3 opensky_cli.py auth-check

# 2. Live Flight Radar by Bounding Box (min_lat min_lon max_lat max_lon)
python3 opensky_cli.py radar --bbox 21.0 105.0 22.5 106.5 --limit 10 --format table

# 3. Live Radar filtered by Callsign or Origin Country
python3 opensky_cli.py radar --country Vietnam --limit 10
python3 opensky_cli.py radar --callsign HVN --format json

# 4. Airport Flights (Arrivals / Departures by ICAO code)
python3 opensky_cli.py flights --airport VVNB --type arrival --limit 15
python3 opensky_cli.py flights --airport ZGGG --type departure

# 5. Aircraft Trajectory Waypoint Track by 24-bit ICAO Hex
python3 opensky_cli.py track --icao24 885142 --limit 20
```

## Features & Architectural Safeguards

- **Single Transport Chokepoint (`opensky/transport.py`)**: All network requests, OAuth2 token renewal, in-memory/disk caching, and quota accounting route through one unified module.
- **1Password OAuth2 Resolver (`opensky/resolver.py`)**: Seamlessly reads credentials from `op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/...` with zero hardcoding. Automatically falls back to environment variables, local `.env`, or anonymous mode (400 credits/day).
- **Self-Healing DNS Fallback**: Transparently resolves `opensky-network.org` via public DNS fallback (`1.1.1.1` / `8.8.8.8`) if regional ISP DNS encounters resolution anomalies.
- **Credit & Rate-Limit Tracking**: Automatically extracts and displays `X-Rate-Limit-Remaining` to protect the 4,000 credit/day allowance.
- **Zero-Dependency Core**: Built with Python 3 standard library (`urllib`, `json`, `dataclasses`, `argparse`).
- **Flexible Formats**: Supports `table` (terminal-friendly aligned columns), `json` (structured machine format for downstream agents), and `csv` (spreadsheet export).

## Programmatic Python SDK Usage

```python
from opensky.api import OpenSkyAPI

# Initializes with auto-resolved credentials (1Password / env / anonymous)
api = OpenSkyAPI()

# 1. Query live aircraft in a geographic box [min_lat, min_lon, max_lat, max_lon]
states = api.get_states(bbox=[21.0, 105.0, 22.5, 106.5])
for s in states:
    print(f"[{s.icao24}] {s.callsign} | {s.origin_country} | Alt: {s.altitude_ft}ft | Speed: {s.speed_kmh}km/h | Status: {'Ground' if s.on_ground else 'Airborne'}")

# 2. Check remaining daily quota credits
status = api.get_rate_limit_status()
print(f"Remaining credits: {status.remaining_credits} / {status.daily_allowance}")
```

## Verification

```bash
# Run 100% offline deterministic test suite (6/6 tests passing)
python3 -m unittest discover -s ~/.gemini/antigravity/skills/opensky-network-cli/tests
```

## 🌐 2nd Brain Travel & Aviation Ecosystem Workflow

| Step | Tool / Skill | Role |
| :--- | :--- | :--- |
| **1. Flight Search & Pricing** | `mcp-flight-search` | Search commercial flight schedules, multi-date fare trends, rail alternatives |
| **2. Live Radar & ADS-B Tracking** | `opensky-network-cli` | Track real-time airborne position, altitude, speed, and airport arrival queues |
| **3. Accommodation** | `agoda-orders-cli` | Historical stay records, hotel pricing intelligence |
| **4. Cost of Living** | `citycost-cli` | Nomad living budget, safety & weather comparison |

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**:
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
- **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
- **NO**: Do nothing.
- **Constraint**: Only log **High-Signal** improvements. Ignore noise.
