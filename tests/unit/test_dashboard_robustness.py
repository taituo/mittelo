from __future__ import annotations

from src.utils.dashboard_snapshot import fetch_dashboard_snapshot


def test_dashboard_snapshot_offline_does_not_raise() -> None:
    # Pick a port that is almost certainly closed; the call must return offline, not crash.
    snap = fetch_dashboard_snapshot("127.0.0.1", 1, timeout_s=0.2, limit=1)
    assert snap.online is False
    assert snap.error

