from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from wrapper.client import JsonlClient


@dataclass(frozen=True)
class DashboardSnapshot:
    online: bool
    stats: dict[str, int]
    tasks: list[dict[str, Any]]
    error: str | None = None


def fetch_dashboard_snapshot(host: str, port: int, *, timeout_s: float = 1.0, limit: int = 20) -> DashboardSnapshot:
    try:
        with JsonlClient(host, port, timeout_s=timeout_s) as c:
            resp_stats = c.call("stats", {})
            stats = dict(resp_stats.get("stats", {}) or {})
            resp_list = c.call("list", {"limit": limit})
            tasks = list(resp_list.get("tasks", []) or [])
        # Normalize stat values to ints.
        stats_norm: dict[str, int] = {}
        for k, v in stats.items():
            try:
                stats_norm[str(k)] = int(v)
            except Exception:
                continue
        return DashboardSnapshot(online=True, stats=stats_norm, tasks=tasks, error=None)
    except Exception as e:
        return DashboardSnapshot(online=False, stats={}, tasks=[], error=str(e))

