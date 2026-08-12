"""CLI — Rich-powered command-line interface for the PC agent."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from task_manager import TaskManager

app = typer.Typer(
    name="agent-bridge",
    help="PC Agent — Monitor and control your servers remotely.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

task_mgr = TaskManager()

server_app = typer.Typer(help="Manage server connections")
task_app = typer.Typer(help="Manage tasks")
service_app = typer.Typer(help="Monitor and control services")

app.add_typer(server_app, name="server")
app.add_typer(task_app, name="task")
app.add_typer(service_app, name="service")


# ── Server ──────────────────────────────────────────────────────────

@server_app.command("add")
def server_add(
    name: Annotated[str, typer.Argument(help="Server nickname")],
    url: Annotated[str, typer.Argument(help="Server URL (http://host:port)")],
    api_key: str = typer.Option("", help="API key for authentication"),
):
    """Register a new server."""
    task_mgr.add_server(name, url, api_key)
    console.print(f"[green]Server '{name}' added ({url})[/green]")


@server_app.command("list")
def server_list():
    """List registered servers."""
    servers = task_mgr.list_servers()
    if not servers:
        console.print("[dim]No servers registered. Use 'server add' to add one.[/dim]")
        return

    table = Table(title="Servers", show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("URL")
    table.add_column("Status", justify="center")
    table.add_column("Last Seen")

    for s in servers:
        status = "[green]Online[/green]" if s.get("online") else "[red]Offline[/red]"
        table.add_row(s["name"], s["url"], status, s.get("last_seen", "Never"))

    console.print(table)


@server_app.command("status")
def server_status(
    name: Annotated[str, typer.Argument(help="Server name")],
):
    """Get detailed server status."""
    data = task_mgr.api_get(name, "/api/v1/status")
    if data is None:
        console.print(f"[red]Could not reach server '{name}'[/red]")
        return

    panel = Panel(
        f"CPU: {data['cpu_percent']}% ({data['cpu_count']} cores)\n"
        f"Load: {data['load_avg_1']:.2f} / {data['load_avg_5']:.2f} / {data['load_avg_15']:.2f}\n"
        f"Memory: {data['memory_used_gb']}GB / {data['memory_total_gb']}GB ({data['memory_percent']}%)\n"
        f"Disk: {data['disk_used_gb']}GB / {data['disk_total_gb']}GB ({data['disk_percent']}%)\n"
        f"Network: ↑{data['net_sent_gb']}GB  ↓{data['net_recv_gb']}GB\n"
        f"Kernel: {data['kernel_version']}",
        title=f"[bold]{data['hostname']}[/bold]",
        border_style="blue",
    )
    console.print(panel)


@server_app.command("remove")
def server_remove(
    name: Annotated[str, typer.Argument(help="Server name to remove")],
):
    """Remove a server."""
    task_mgr.remove_server(name)
    console.print(f"[yellow]Server '{name}' removed[/yellow]")


# ── Tasks ───────────────────────────────────────────────────────────

@task_app.command("run")
def task_run(
    server: Annotated[str, typer.Argument(help="Server name")],
    command: Annotated[str, typer.Argument(help="Command to execute")],
    title: str = typer.Option("CLI Command", help="Task title"),
):
    """Execute a command on a remote server."""
    result = task_mgr.run_command(server, command, title=title)
    console.print(f"[bold]{result['title']}[/bold]")
    if result.get("exit_code") == 0:
        console.print(f"[green]✓ Exit code: 0[/green]")
    else:
        console.print(f"[red]✗ Exit code: {result.get('exit_code', '?')}[/red]")
    if result.get("stdout"):
        console.print(result["stdout"])
    if result.get("stderr"):
        console.print(f"[red]{result['stderr']}[/red]")


@task_app.command("list")
def task_list(
    server: Annotated[str, typer.Argument(help="Server name")],
    status: str = typer.Option(None, help="Filter by status"),
):
    """List tasks on a server."""
    data = task_mgr.api_get(server, "/api/v1/tasks", params={"status": status})
    if data is None:
        console.print(f"[red]Could not reach '{server}'[/red]")
        return

    table = Table(title=f"Tasks — {server}", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Assigned To")
    table.add_column("Created")

    for t in data:
        status_color = {
            "completed": "green",
            "running": "yellow",
            "failed": "red",
            "pending": "dim",
        }.get(t["status"], "white")
        table.add_row(
            t["id"],
            t["title"],
            f"[{status_color}]{t['status']}[/{status_color}]",
            t.get("assigned_to", ""),
            t.get("created_at", "")[:19],
        )

    console.print(table)


# ── Services ────────────────────────────────────────────────────────

@service_app.command("list")
def service_list(
    server: Annotated[str, typer.Argument(help="Server name")],
):
    """List monitored services."""
    data = task_mgr.api_get(server, "/api/v1/services")
    if data is None:
        console.print(f"[red]Could not reach '{server}'[/red]")
        return

    table = Table(title=f"Services — {server}", show_lines=True)
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Status", justify="center")
    table.add_column("PID")
    table.add_column("CPU%", justify="right")
    table.add_column("Memory", justify="right")

    for svc in data:
        status_color = {
            "active": "green",
            "inactive": "red",
            "activating": "yellow",
            "deactivating": "yellow",
            "unknown": "dim",
        }.get(svc["status"], "white")
        table.add_row(
            svc["name"],
            svc["type"],
            f"[{status_color}]{svc['status']}[/{status_color}]",
            str(svc.get("pid") or ""),
            f"{svc.get('cpu_percent', 0):.1f}%",
            f"{svc.get('memory_mb', 0):.1f}MB",
        )

    console.print(table)


@service_app.command("restart")
def service_restart(
    server: Annotated[str, typer.Argument(help="Server name")],
    name: Annotated[str, typer.Argument(help="Service name")],
):
    """Restart a service on the server."""
    result = task_mgr.api_post(server, f"/api/v1/services/{name}/restart")
    if result:
        console.print(f"[green]Service '{name}' restarted[/green]")
    else:
        console.print(f"[red]Failed to restart '{name}'[/red]")


@service_app.command("watch")
def service_watch(
    server: Annotated[str, typer.Argument(help="Server name")],
    name: Annotated[str, typer.Argument(help="Service name to watch")],
):
    """Add a service to the monitor watch list."""
    result = task_mgr.api_post(server, f"/api/v1/services/{name}/watch")
    if result:
        console.print(f"[green]Now watching '{name}' on {server}[/green]")


# ── Main ────────────────────────────────────────────────────────────

@app.command("status")
def main_status():
    """Quick overview of all servers."""
    servers = task_mgr.list_servers()
    if not servers:
        console.print("[dim]No servers configured.[/dim]")
        return

    for s in servers:
        status = "[green]Online[/green]" if s.get("online") else "[red]Offline[/red]"
        console.print(f"  {s['name']} ({s['url']}): {status}")


@app.command("dashboard")
def dashboard(
    server: Annotated[str, typer.Argument(help="Server name")],
):
    """Interactive dashboard (launches monitor)."""
    from monitor_dashboard import run_dashboard
    run_dashboard(task_mgr, server)


@app.command("config")
def show_config():
    """Show current PC agent configuration."""
    task_mgr.print_config()
