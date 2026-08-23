# Troubleshooting for Feishu / Lark CLI Operator

Recovery paths kept out of `SKILL.md` so the main skill stays lightweight.

## Known Issues & Solutions

| Symptom | Cause | Solution |
|---------|-------|----------|
| `command not found` or `FileNotFoundError` when executing `lark-cli` | A Node or package-manager upgrade can leave the globally-installed `lark-cli` shim missing or pointing at a removed version directory. | Reinstall with `npm install -g @larksuite/cli`, or install the version-independent wrapper below. |
| `npx` exits before running a package after a Node upgrade | The `npx` shim can point at a missing npm-prefix helper even though Node and the bundled npm module still exist. | Invoke `npx-cli.js` through the active `node` binary, as the wrapper below does. |
| `Operation not permitted` (exit code 126) inside a sandboxed agent runtime | Agent sandboxes commonly block `node`/`npx` execution and outbound network access to Feishu/Lark endpoints. | Re-run outside the sandbox, or use the runtime's documented escape hatch after explicit user approval. Do not weaken the sandbox globally to fix one command. |
| Exit code `10` with `error.subtype == "confirmation_required"` | A high-risk write was called without `--yes`. This is the safety gate working. | Surface the pending operation to the user, get explicit approval, then retry with `--yes` appended. Never retry automatically. |
| Exit code `2` with `error.type == "validation"` | An unknown or malformed flag. | Check `lark-cli <command> --help`. Note that a flag which *parses* is not necessarily a flag that *does* anything — see the `--api-version` note in `SKILL.md`. |
| `config init` refuses to run | An agent workspace is active (`OPENCLAW_HOME` / `HERMES_HOME` set) and the CLI is steering you away from creating a parallel app. | Use `lark-cli config bind` to bind to the existing app. Pass `--force-init` only if a separate app is genuinely wanted. |

## Version-Independent Wrapper

If scripts invoke `lark-cli` directly and the global shim keeps breaking across
Node upgrades, install this wrapper somewhere on `PATH` — `~/.local/bin/lark-cli`
is a good default — and make it executable with `chmod +x`.

It resolves npm's own `npx-cli.js` through whichever `node` is active, so it
does not hardcode a Homebrew, nvm, Volta, or system install path:

```sh
#!/bin/sh
# Compatibility wrapper: run the official Feishu/Lark CLI through the active
# Node runtime, tolerating a broken or missing `npx` shim.
NODE_BIN=${LARK_CLI_NODE:-$(command -v node 2>/dev/null)}
if [ -z "$NODE_BIN" ]; then
  echo "lark-cli: no node found on PATH (set LARK_CLI_NODE)" >&2
  exit 127
fi

# npm ships its own npx entrypoint next to the node install; the `npx` shim is
# what breaks after an upgrade, so resolve npx-cli.js directly.
NPX_CLI=$("$NODE_BIN" -e 'const p=require("path"),f=require("fs");const c=p.join(p.dirname(process.execPath),"..","lib","node_modules","npm","bin","npx-cli.js");if(f.existsSync(c))console.log(f.realpathSync(c));' 2>/dev/null)

if [ -z "$NPX_CLI" ]; then
  NPM_GLOBAL_ROOT=$(npm root -g 2>/dev/null)
  [ -n "$NPM_GLOBAL_ROOT" ] && [ -f "$NPM_GLOBAL_ROOT/npm/bin/npx-cli.js" ] \
    && NPX_CLI="$NPM_GLOBAL_ROOT/npm/bin/npx-cli.js"
fi

if [ -z "$NPX_CLI" ] || [ ! -f "$NPX_CLI" ]; then
  echo "lark-cli: could not locate npx-cli.js for $NODE_BIN" >&2
  exit 127
fi

exec "$NODE_BIN" "$NPX_CLI" --yes @larksuite/cli "$@"
```

Set `LARK_CLI_NODE` to pin a specific Node binary when several are installed.
Point `LARK_CLI_BIN` (or your project's adapter variable) at the wrapper path
if tooling needs an explicit location.

Verify the wrapper resolves before trusting it:

```sh
lark-cli --help          # should print the CLI's top-level help
lark-cli doctor          # config, auth, and connectivity health check
```

Do not print OAuth tokens, app secrets, or raw config while diagnosing the
wrapper. `lark-cli doctor` and `lark-cli whoami` report health and identity
status without dumping credentials — prefer them over reading config files by
hand.
