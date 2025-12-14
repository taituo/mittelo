from __future__ import annotations

import os
from pathlib import Path

from src.wrapper.backends import resolve_backend_argv


def test_resolve_backend_argv_echo_points_to_run() -> None:
    argv = resolve_backend_argv("echo")
    assert argv is not None
    assert argv[-1].endswith(str(Path("backends") / "echo" / "run"))


def test_resolve_backend_argv_respects_mittelo_backends_dir(tmp_path: Path) -> None:
    # Create an alternate backend folder.
    alt = tmp_path / "backends"
    (alt / "alt_echo").mkdir(parents=True)
    (alt / "alt_echo" / "run").write_text("#!/usr/bin/env bash\necho alt\n", encoding="utf-8")

    old = os.environ.get("MITTELO_BACKENDS_DIR")
    os.environ["MITTELO_BACKENDS_DIR"] = str(alt)
    try:
        argv = resolve_backend_argv("alt_echo")
        assert argv is not None
        assert argv[-1] == str(alt / "alt_echo" / "run")
    finally:
        if old is None:
            os.environ.pop("MITTELO_BACKENDS_DIR", None)
        else:
            os.environ["MITTELO_BACKENDS_DIR"] = old

