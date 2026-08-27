# Changelog - `opensky-network-cli`

## [1.0.0] - 2026-08-27

### Added
- **Unified Core & Transport**: Single chokepoint (`opensky/transport.py`) for OAuth2 Bearer token lifecycle, in-memory & disk token caching (30m TTL), and live `X-Rate-Limit-Remaining` header parsing.
- **Self-Healing DNS Fallback**: Transparent `1.1.1.1` / `8.8.8.8` DNS resolution hook in `opensky/transport.py` preventing failures on regional DNS anomalies.
- **1Password OAuth2 Resolver**: Automated resolution from `op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/...` with fallback to `.env`, environment variables, and anonymous mode (400 credits/day vs 4,000 credits/day).
- **CLI Commands**:
  - `auth-check` / `quota`: Inspects credential resolution, token validity, and remaining daily credit.
  - `radar` / `states`: Real-time aircraft positions with `--bbox`, `--callsign`, `--country`, `--icao24`, and formatters (`table`, `json`, `csv`).
  - `flights`: Airport arrivals/departures and aircraft flight history.
  - `track`: Trajectory waypoints by 24-bit ICAO address.
- **Deterministic Unit Tests**: 6 offline tests covering model parsing, unit conversions, and mocked rate-limit accounting.
- **Ecosystem Registration**: Registered in `00 - System/registries/project-capabilities.md`.
