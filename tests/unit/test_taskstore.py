from __future__ import annotations

import time
from pathlib import Path

from orchestrator.storage import TaskStore


def test_enqueue_lease_ack_and_list(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    store = TaskStore(str(db_path))
    try:
        tid = store.enqueue("hello")
        tasks = store.lease(worker_id="w1", max_tasks=1, lease_seconds=60)
        assert [t.task_id for t in tasks] == [tid]
        store.ack(task_id=tid, status="done", result="ok", error=None)

        got = store.list(status="done", limit=10)
        assert len(got) == 1
        assert got[0].task_id == tid
        assert got[0].result == "ok"
        assert got[0].error is None
    finally:
        store.close()


def test_lease_requeues_expired(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    store = TaskStore(str(db_path))
    try:
        tid = store.enqueue("hello")
        _ = store.lease(worker_id="w1", max_tasks=1, lease_seconds=60)

        # Force expire the lease.
        now = time.time()
        with store._lock:  # type: ignore[attr-defined]
            cur = store._db.cursor()  # type: ignore[attr-defined]
            cur.execute(
                "UPDATE tasks SET leased_until=?, status='leased' WHERE task_id=?",
                (now - 10, tid),
            )
            store._db.commit()  # type: ignore[attr-defined]

        tasks2 = store.lease(worker_id="w2", max_tasks=1, lease_seconds=60)
        assert len(tasks2) == 1
        assert tasks2[0].task_id == tid
        assert tasks2[0].worker_id == "w2"
    finally:
        store.close()


def test_retry_all_failed(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    store = TaskStore(str(db_path))
    try:
        tid = store.enqueue("hello")
        _ = store.lease(worker_id="w1", max_tasks=1, lease_seconds=60)
        store.ack(task_id=tid, status="failed", result=None, error="boom")

        retried = store.retry_all_failed()
        assert retried == 1

        queued = store.list(status="queued", limit=10)
        assert len(queued) == 1
        assert queued[0].task_id == tid
        assert queued[0].result is None
        assert queued[0].error is None
        assert queued[0].worker_id is None
    finally:
        store.close()


def test_list_limit_zero_means_no_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    store = TaskStore(str(db_path))
    try:
        for i in range(5):
            store.enqueue(f"t{i}")
        got = store.list(status=None, limit=0)
        assert len(got) == 5
    finally:
        store.close()

