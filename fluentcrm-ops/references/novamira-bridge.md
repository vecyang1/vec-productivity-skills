# Novamira Bridge Notes

This skill uses the existing `novamira-ops` bridge instead of reimplementing WordPress MCP.

## Credential Lookup

`scripts/fluentcrm_ops.py` imports `novamira-ops/scripts/wp_ops.py`. That bridge loads credentials in this order:

1. Current environment: `WP_API_URL`, `WP_API_USERNAME`, `WP_API_PASSWORD`
2. Local `.env`
3. `~/.gemini/antigravity/mcp_config.json`, choosing a server name containing `novamira` or `wordpress`

Use `NOVAMIRA_WP_OPS=/path/to/wp_ops.py` if the bridge is installed somewhere else.

## Why CLI For Codex

Antigravity may expose Novamira as MCP tools, but Codex sessions often need a shell-first interface. The CLI performs the MCP initialization handshake by reusing `wp_ops.py`, then routes all operations through `mcp-adapter-execute-ability`.

`fluentcrm_ops.py` normalizes the common Novamira response envelopes before printing results:

- `{"success": true, "data": {"return_value": ...}}` becomes the `return_value`.
- `{"success": true, "data": ...}` becomes `data`.
- Error or unknown shapes stay raw so troubleshooting detail is not hidden.

## Troubleshooting

- Missing bridge: install or symlink `novamira-ops`, or set `NOVAMIRA_WP_OPS`.
- Missing credentials: check environment, `.env`, then `~/.gemini/antigravity/mcp_config.json`.
- `Missing Mcp-Session-Id header`: do not call the endpoint directly; use the bridge.
- PHP crash/safe mode: use the `novamira-ops` troubleshooting reference and avoid writing PHP files unless needed.
