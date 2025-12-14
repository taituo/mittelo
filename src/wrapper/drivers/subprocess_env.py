from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional


def build_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build a subprocess environment for external CLIs.

    If `MITTELO_SUBPROCESS_HOME` is set, we redirect HOME + XDG dirs there so
    CLIs can run in sandboxed environments where writing to the real home is blocked.
    """
    env: Dict[str, str] = dict(os.environ)
    home = env.get("MITTELO_SUBPROCESS_HOME")
    if home:
        home_path = Path(home)
        home_path.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(home_path)
        env.setdefault("XDG_CONFIG_HOME", str(home_path / ".config"))
        env.setdefault("XDG_DATA_HOME", str(home_path / ".local" / "share"))
        env.setdefault("XDG_STATE_HOME", str(home_path / ".local" / "state"))
        Path(env["XDG_CONFIG_HOME"]).mkdir(parents=True, exist_ok=True)
        Path(env["XDG_DATA_HOME"]).mkdir(parents=True, exist_ok=True)
        Path(env["XDG_STATE_HOME"]).mkdir(parents=True, exist_ok=True)

    if extra:
        env.update(extra)
    return env

