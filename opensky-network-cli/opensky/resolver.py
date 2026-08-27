"""
Credential resolver for OpenSky Network OAuth2 and API access.
Resolves credentials in priority:
1. 1Password item reference (op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/...)
2. Environment variables (OPENSKY_CLIENT_ID, OPENSKY_CLIENT_SECRET)
3. Local .env file
4. Anonymous fallback (400 credits/day standard)
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_1P_CLIENT_ID_REF = "op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/username"
DEFAULT_1P_CLIENT_SECRET_REF = "op://Agent Automation/2pespkd44vu2zoxvlitgcbybeq/credential"


def _read_from_1password(reference: str, timeout_sec: float = 4.0) -> Optional[str]:
    """Read secret via 1Password CLI using op read --no-newline."""
    op_path = shutil.which("op")
    if not op_path:
        return None
    try:
        proc = subprocess.run(
            [op_path, "read", reference, "--no-newline"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except Exception:
        pass
    return None


def _read_from_dotenv(env_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Parse key=value pairs from a .env file."""
    client_id = None
    client_secret = None
    if not env_path.is_file():
        return None, None
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k in ("OPENSKY_CLIENT_ID", "OPENSKY_USERNAME"):
                        client_id = v
                    elif k in ("OPENSKY_CLIENT_SECRET", "OPENSKY_PASSWORD"):
                        client_secret = v
    except Exception:
        pass
    return client_id, client_secret


def resolve_credentials(
    custom_client_id: Optional[str] = None,
    custom_client_secret: Optional[str] = None,
    skill_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Resolve OpenSky credentials.
    Returns: (client_id, client_secret, source_description)
    """
    if custom_client_id and custom_client_secret:
        return custom_client_id, custom_client_secret, "explicit_arguments"

    # 1. Environment variables
    env_id = os.environ.get("OPENSKY_CLIENT_ID") or os.environ.get("OPENSKY_USERNAME")
    env_secret = os.environ.get("OPENSKY_CLIENT_SECRET") or os.environ.get("OPENSKY_PASSWORD")
    if env_id and env_secret:
        return env_id, env_secret, "environment_variables"

    # 2. 1Password CLI reference
    one_pass_id = _read_from_1password(DEFAULT_1P_CLIENT_ID_REF)
    one_pass_secret = _read_from_1password(DEFAULT_1P_CLIENT_SECRET_REF)
    if one_pass_id and one_pass_secret:
        return one_pass_id, one_pass_secret, "1password_vault"

    # 3. Local skill .env file
    target_dirs = []
    if skill_dir:
        target_dirs.append(skill_dir)
    target_dirs.extend([
        Path(__file__).resolve().parent.parent,
        Path.cwd(),
    ])
    for d in target_dirs:
        env_file = d / ".env"
        f_id, f_secret = _read_from_dotenv(env_file)
        if f_id and f_secret:
            return f_id, f_secret, f"dotenv_file:{env_file}"

    # 4. Anonymous fallback
    return None, None, "anonymous"
