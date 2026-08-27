# Agent Constitution for `opensky-network-cli`

## Single Chokepoint Policy
- **DO NOT** make direct HTTP calls to OpenSky Network outside of `opensky/transport.py`.
- `opensky/transport.py` owns OAuth2 client credentials token exchange, Bearer token caching, DNS resilience, and daily quota accounting.

## Credential Safety
- Never hardcode Client ID or Client Secret.
- Always use `opensky/resolver.py` to retrieve credentials from 1Password or `.env`.

## Deterministic Testing
- Run `python3 -m unittest discover -s tests` before claiming any modification is complete.
