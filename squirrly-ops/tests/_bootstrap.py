"""Single owner for test isolation. Every test module imports this FIRST.

Two jobs, and the ordering matters for both:

* Point every location variable at a disposable directory **before** the code
  under test is imported, so a test can never read or write the real registry
  at ~/.config/squirrly-ops/sites.json. Location variables are set to a sandbox
  rather than deleted: unset does not mean "use nothing", it means "use the
  default", and the default here is the live file.
* Scrub credential variables, where absent genuinely is the state we want.

One owner per process, so the import cache deduplicates it. Per-module sandboxes
would each create their own temp dir and only the first to load would be real.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

SANDBOX = Path(tempfile.mkdtemp(prefix="squirrly-ops-tests-"))
REAL_CONFIG = Path.home() / ".config" / "squirrly-ops" / "sites.json"

# locations -> sandbox (structural isolation, not a mock anyone must remember)
os.environ["SQUIRRLY_OPS_CONFIG"] = str(SANDBOX / "sites.json")

# credentials -> absent
for _name in ("SQUIRRLY_API_TOKEN", "OP_SERVICE_ACCOUNT_TOKEN"):
    os.environ.pop(_name, None)

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def load(module_name: str):
    """Import a script by path; scripts/ is not an importable package."""
    path = SCRIPTS / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def write_registry(payload: str, name: str = "sites.json") -> str:
    target = SANDBOX / name
    target.write_text(payload, encoding="utf-8")
    return str(target)
