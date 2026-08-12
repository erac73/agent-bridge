"""Monitor Dashboard — Rich live dashboard for server monitoring."""

from __future__ import annotations

import time

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from task_manager import TaskManager


def make_header(server_name: str) -> Panel:
    return Panel(
        f"[bold white]Agent Bridge Dashboard — {server_name}[/bold white]",
        style="blue",
    )


def make_system_panel(data: dict) -> Panel:
    cpu = data.get("cpu_percent", 0)
    mem = data.get("memory_percent", 0)
    disk = data.get("disk_percent", 0)

    cpu_color = "green" if cpu < 70 else "yellow" if cpu < 90 else "red"
    mem_color = "green" if mem < 70 else "yellow" if mem < 90 else "red"
    disk_color = "green" if disk < 80 else "yellow" if disk < 90 else "red"

    content = (
        f"[{cpu_color}]CPU:     {cpu:5.1f}%[/]\n"
        f"[{mem_color}]Memory:  {data.get('memory_used_gb', 0)}/{data.get('memory_total_gb', 0)} GB ({mem:.1f}%)[/]\n"
        f"[{disk_color}]Disk:    {data.get('disk_used_gb', 0)}/{data.get('disk_total_gb', 0)} GB ({disk:.1f}%)[/]\n"
        f"Network:  ↑{data.get('net_sent_gb', 0)} GB  ↓{data.get('net_recv_gb', 0)} GB\n"
        f"Load:    {data.get('load_avg_1', 0):.2f} / {data.get('load_avg_5', 0):.2f} / {data.get('load_avg_15', 0):.2f}"
    )

    return Panel(content, title="[bold]System[/bold]", border_style="green")


def make_services_panel(services: list) -> Panel:
    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Service", ratio=2)
    table.add_column("Status", ratio=1)
    table.add_column("Type", ratio=1)
    table.add_column("PID", ratio=1)

    for svc in services:
        status = svc.get("status", "unknown")
        color = {
            "active": "green", "inactive": "red",
            "activating": "yellow", "unknown": "dim",
        }.get(status, "white")
        table.add_row(
            svc.get("name", "?"),
            f"[{color}]{status}[/{color}]",
            svc.get("type", ""),
            str(svc.get("pid") or ""),
        )

    return Panel(table, title="[bold]Services[/bold]", border_style="blue")


def make_alerts_panel(alerts: list) -> Panel:
    if not alerts:
        return Panel("[dim]No active alerts[/dim]", title="[bold]Alerts[/bold]", border_style="dim")

    lines = []
    for a in alerts[-10:]:
        severity_color = {
            "critical": "bold red", "error": "red",
            "warning": "yellow", "info": "dim",
        }.get(a.get("severity", ""), "white")
        lines.append(f"[{severity_color}]• [{a.get('severity', '').upper()}][/] {a.get('title', '')}: {a.get('message', '')}")

    return Panel("\n".join(lines), title="[bold]Alerts[/bold]", border_style="yellow")


def make_layout(data: dict) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )
    layout["left"].split_column(
        Layout(name="system"),
        Layout(name="services"),
    )

    alerts = data.get("alerts", [])
    layout["header"].update(make_header(data.get("hostname", "unknown")))
    layout["system"].update(make_system_panel(data))
    layout["services"].update(make_services_panel(data.get("services", [])))
    layout["right"].update(make_alerts_panel(alerts))

    return layout


def run_dashboard(task_mgr: TaskManager, server_name: str, refresh: int = 5):
    console = Console()

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            status = task_mgr.api_get(server_name, "/api/v1/status")
            alerts = task_mgr.api_get(server_name, "/api/v1/alerts") or []

            if status is None:
                console.print(f"[red]Lost connection to '{server_name}'[/red]")
                break

            status["alerts"] = alerts
            layout = make_layout(status)
            live.update(layout)
            time.sleep(refresh)
