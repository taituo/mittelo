from __future__ import annotations

from pathlib import Path

from orchestrator.server import JsonlHubHandler, _HubState
from orchestrator.storage import TaskStore


def test_dispatch_enqueue_list_stats(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    store = TaskStore(str(db_path))
    try:
        state = _HubState(store, lease_seconds=60)
        handler = JsonlHubHandler.__new__(JsonlHubHandler)

        res = JsonlHubHandler._dispatch(handler, state, "enqueue", {"prompt": "hello"})
        tid = int(res["task_id"])

        stats = JsonlHubHandler._dispatch(handler, state, "stats", {})
        assert stats["stats"]["queued"] >= 1

        listed = JsonlHubHandler._dispatch(handler, state, "list", {"limit": 10})
        assert any(int(t["task_id"]) == tid for t in listed["tasks"])
    finally:
        store.close()

