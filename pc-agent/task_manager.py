"""Task Manager — Manages servers, tasks, and API communication."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
import yaml

CONFIG_PATH = Path.home() / ".config" / "agent-bridge" / "config.yaml"


class TaskManager:
    """Manages server registry, tasks, and API communication."""

    def __init__(self):
        self._config = self._load_config()
        self._servers: dict[str, dict] = self._config.get("servers", {})
        self._http = httpx.Client(timeout=30)

    def _load_config(self) -> dict:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                return yaml.safe_load(f) or {}
        return {"servers": {}}

    def _save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(
                {"servers": self._servers},
                f,
                default_flow_style=False,
            )

    def _get_server(self, name: str) -> dict:
        if name not in self._servers:
            raise ValueError(f"Server '{name}' not found")
        return self._servers[name]

    def add_server(self, name: str, url: str, api_key: str = ""):
        self._servers[name] = {
            "name": name,
            "url": url.rstrip("/"),
            "api_key": api_key,
            "online": False,
            "last_seen": None,
        }
        self._save_config()

    def remove_server(self, name: str):
        self._servers.pop(name, None)
        self._save_config()

    def list_servers(self) -> list[dict]:
        result = []
        for name, srv in self._servers.items():
            try:
                resp = self._http.get(f"{srv['url']}/health/live", timeout=5)
                srv["online"] = resp.status_code == 200
                srv["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                srv["online"] = False
            result.append(srv)
        return result

    def api_get(
        self, server_name: str, path: str, params: dict | None = None
    ) -> Any:
        srv = self._get_server(server_name)
        headers = self._auth_headers(srv)
        try:
            resp = self._http.get(
                f"{srv['url']}{path}",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def api_post(
        self, server_name: str, path: str, json_data: Any = None
    ) -> Any:
        srv = self._get_server(server_name)
        headers = self._auth_headers(srv)
        try:
            resp = self._http.post(
                f"{srv['url']}{path}",
                json=json_data,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def run_command(
        self,
        server_name: str,
        command: str,
        title: str = "CLI Command",
        timeout: int = 60,
    ) -> dict:
        srv = self._get_server(server_name)
        headers = self._auth_headers(srv)
        parts = command.split()

        try:
            resp = self._http.post(
                f"{srv['url']}/api/v1/command",
                json={
                    "command": parts[0],
                    "args": parts[1:],
                    "timeout_seconds": timeout,
                },
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()
            result["title"] = title
            return result
        except Exception as e:
            return {
                "title": title,
                "exit_code": -1,
                "error": str(e),
            }

    def _auth_headers(self, srv: dict) -> dict[str, str]:
        if srv.get("api_key"):
            return {"Authorization": f"Bearer {srv['api_key']}"}
        return {}

    def print_config(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Configuration")
        table.add_column("Key", style="bold")
        table.add_column("Value")

        table.add_row("Config Path", str(CONFIG_PATH))
        table.add_row("Servers", str(len(self._servers)))

        for name, srv in self._servers.items():
            table.add_row(f"  {name}", srv["url"])

        console.print(table)
