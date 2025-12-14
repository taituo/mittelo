from dataclasses import dataclass
from unittest.mock import MagicMock
from orchestrator.server import JsonlHubHandler, _HubState

@dataclass
class Task:
    task_id: int
    status: str = "queued"

def _create_handler(store_mock):
    """Helper to create a handler with a mocked state, avoiding __init__ side effects."""
    state = _HubState(store_mock, lease_seconds=60)
    # Use __new__ to bypass StreamRequestHandler.__init__ (which requires a real socket)
    handler = JsonlHubHandler.__new__(JsonlHubHandler)
    handler.server = MagicMock() # type: ignore
    return handler, state

def test_dispatch_enqueue():
    mock_store = MagicMock()
    mock_store.enqueue.return_value = 123
    handler, state = _create_handler(mock_store)
    
    result = handler._dispatch(state, "enqueue", {"prompt": "test"})
    
    mock_store.enqueue.assert_called_with("test")
    assert result == {"task_id": 123}

def test_dispatch_list_default():
    mock_store = MagicMock()
    mock_store.list.return_value = []
    mock_store.stats.return_value = {}
    handler, state = _create_handler(mock_store)
    
    handler._dispatch(state, "list", {})
    
    # Verify default limit is 50
    mock_store.list.assert_called_with(status=None, limit=50)

def test_dispatch_list_zero():
    mock_store = MagicMock()
    mock_store.list.return_value = [Task(task_id=i) for i in range(5)]
    mock_store.stats.return_value = {}
    handler, state = _create_handler(mock_store)
    
    result = handler._dispatch(state, "list", {"limit": 0})
    
    # Verify limit=0 is passed explicitly
    mock_store.list.assert_called_with(status=None, limit=0)
    assert len(result["tasks"]) == 5

def test_dispatch_stats():
    mock_store = MagicMock()
    mock_store.stats.return_value = {"queued": 1}
    handler, state = _create_handler(mock_store)
    
    result = handler._dispatch(state, "stats", {})
    
    assert result == {"stats": {"queued": 1}}
