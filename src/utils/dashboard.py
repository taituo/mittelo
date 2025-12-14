import json
import time
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import Header, Footer, Static, DataTable, Digits
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text

# Import Client (adjust path as needed)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.wrapper.client import JsonlClient

# Load Small Logo
LOGO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo_small.ansi"))
try:
    with open(LOGO_PATH, "r") as f:
        MITTELO_LOGO = f.read()
except FileNotFoundError:
    MITTELO_LOGO = "LOGO M.I.A."

BBS_INFO = """
 [bold white]MITTELO SWARM CONTROL v1.0[/]
 [dim]--------------------------[/]
 [cyan]SYSOP:[/cyan] [bold yellow]GEMINI[/]
 [cyan]NODE:[/cyan]  [bold yellow]LOCAL/DEV[/]
 [cyan]BAUD:[/cyan]  [bold green]INFINITE[/]
 [dim]--------------------------[/]
 [italic]"The Swarm is Watching."[/]
"""

class StatBox(Static):
    """A widget to display a single statistic."""
    value = reactive(0)

    def __init__(self, label: str, id: str, color: str = "white"):
        super().__init__(id=id)
        self.label = label
        self.color = color

    def compose(self) -> ComposeResult:
        yield Static(self.label, classes="stat-label")
        self.digits = Static(str(self.value), classes="stat-value")
        self.digits.styles.color = self.color
        yield self.digits

    def watch_value(self, new_value: int) -> None:
        if hasattr(self, "digits"):
            self.digits.update(str(new_value))

class MitteloDash(App):
    """Mittelö Swarm Mission Control."""

    CSS = """
    Screen {
        layout: vertical;
        background: #0f111a;
    }
    
    /* ... header styles ... */

    .stat-value {
        text-align: center;
        content-align: center middle;
        width: 100%;
        height: 1fr;
        text-style: bold;
    }


    .header-container {
        layout: horizontal;
        height: auto;
        min-height: 8;
        margin-bottom: 1;
        border-bottom: solid #00b8ff;
        background: #1a1d2d;
    }

    .logo-box {
        width: 45;
        height: 100%;
        background: #000000;
        align: center middle;
    }

    .info-box {
        width: 1fr;
        height: 100%;
        content-align: left middle;
        padding-left: 2;
        color: #00ff9f;
    }

    .stat-grid {
        layout: grid;
        grid-size: 4;
        grid-gutter: 1;
        height: 10;
        margin: 1;
    }

    StatBox {
        background: #1a1d2d;
        border: wide #00ff9f;
        padding: 1;
        align: center middle;
    }

    .stat-label {
        text-align: center;
        width: 100%;
        color: #a0a0a0;
        text-style: bold;
    }

    DataTable {
        height: 1fr;
        border: wide #00b8ff;
        margin: 1;
        background: #0f111a;
    }
    
    DataTable > .datatable--header {
        background: #1a1d2d;
        color: #00ff9f;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Now"),
    ]

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.host = host
        self.port = port
        self.client = None
        self.connected = False

    def compose(self) -> ComposeResult:
        # BBS Header
        with Container(classes="header-container"):
             yield Static(Text.from_ansi(MITTELO_LOGO), classes="logo-box")
             yield Static(BBS_INFO, classes="info-box")
        
        with Container(classes="stat-grid"):
            yield StatBox("QUEUED", id="stat-queued", color="#ffbd2e")
            yield StatBox("LEASED", id="stat-leased", color="#00b8ff")
            yield StatBox("DONE", id="stat-done", color="#00ff9f")
            yield StatBox("DONE", id="stat-done", color="#00ff9f")
            yield StatBox("FAILED", id="stat-failed", color="#ff5f56")
            yield StatBox("STATUS", id="stat-status", color="#aaaaaa")

        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Mittelö Swarm Control"
        self.table = self.query_one(DataTable)
        self.table.add_columns("ID", "Status", "Prompt", "Worker", "Result")
        self.table.cursor_type = "row"
        self.table.zebra_stripes = True
        self.set_interval(1.0, self.update_stats)

    def action_refresh(self) -> None:
        self.update_stats()

    def update_stats(self) -> None:
        try:
            with JsonlClient(self.host, self.port, timeout_s=1.0) as c:
                resp_stats = c.call("stats", {})
                s = resp_stats.get("stats", {})
                
                self.query_one("#stat-queued", StatBox).value = s.get("queued", 0)
                self.query_one("#stat-leased", StatBox).value = s.get("leased", 0)
                self.query_one("#stat-done", StatBox).value = s.get("done", 0)
                self.query_one("#stat-failed", StatBox).value = s.get("failed", 0)
                
                self.connected = True
                self.query_one("#stat-status", StatBox).value = "ONLINE"
                self.query_one("#stat-status", StatBox).digits.styles.color = "#00ff00"

                resp_list = c.call("list", {"limit": 20})
                tasks = resp_list.get("tasks", [])
                
                self.table.clear()
                for t in tasks:
                    t_id = str(t["task_id"])
                    status = t["status"]
                    prompt = t["prompt"][:50].replace("\n", " ") + "..."
                    worker = (t["worker_id"] or "-").split("-")[1] if "-" in (t["worker_id"] or "") else "-"
                    result = (t["result"] or "")[:50].replace("\n", " ") + "..."
                    
                    if status == "done": 
                        status_styled = "[bold green]✔ DONE[/]"
                    elif status == "failed": 
                        status_styled = "[bold red]✘ FAIL[/]"
                    elif status == "leased": 
                        status_styled = "[bold cyan]⟳ RUN [/]"
                    elif status == "queued": 
                        status_styled = "[bold yellow]● WAIT[/]"
                    else:
                        status_styled = status

                    self.table.add_row(t_id, status_styled, prompt, worker, result)

        except Exception as e:
            self.connected = False
            self.sub_title = f"Error: {e}"
            self.query_one("#stat-status", StatBox).value = "OFFLINE"
            self.query_one("#stat-status", StatBox).digits.styles.color = "#ff0000"

def run_dashboard(host, port):
    app = MitteloDash(host, port)
    app.run()
