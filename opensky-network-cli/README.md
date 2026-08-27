# OpenSky Network CLI (`opensky-network-cli`)

A unified command-line interface and Python SDK for querying OpenSky Network ADS-B real-time flight telemetry, state vectors, airport arrivals/departures, and aircraft trajectory paths.

## Key Capabilities
- Real-time global aircraft radar telemetry (`states/all`).
- 1Password OAuth2 credential resolver (`op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/...`).
- Transport chokepoint with rate-limit tracking (`X-Rate-Limit-Remaining`) and token caching.
- Self-healing DNS fallback resolution (`1.1.1.1` / `8.8.8.8`).
- 100% offline deterministic unit tests.

## Quickstart
```bash
python3 opensky_cli.py auth-check
python3 opensky_cli.py radar --bbox 21.0 105.0 22.5 106.5 --limit 10
python3 opensky_cli.py flights --airport VVNB --type arrival
```
