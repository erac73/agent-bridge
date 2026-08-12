"""Service Monitor — Watches systemd, Docker, and process health."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import psutil

from shared.models import Alert, AlertSeverity, ServiceInfo, ServiceStatus

logger = logging.getLogger("server-agent.monitor")


class ServiceMonitor:
    """Continuously monitors system services and generates alerts."""

    def __init__(self, interval: int = 15):
        self._interval = interval
        self._thread: threading.Thread | None = None
        self._running = False
        self._services: dict[str, ServiceInfo] = {}
        self._alerts: list[Alert] = []
        self._watched_services: list[str] = []

    def start(self):
        """Start the monitoring thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(f"Service monitor started (interval={self._interval}s)")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def watch_service(self, name: str):
        """Add a service to the watch list."""
        if name not in self._watched_services:
            self._watched_services.append(name)
            logger.info(f"Now watching: {name}")

    def _loop(self):
        while self._running:
            try:
                self._check_services()
                self._check_resources()
            except Exception as e:
                logger.error(f"Monitor check failed: {e}")
            time.sleep(self._interval)

    def _check_services(self):
        """Check status of all watched services."""
        for name in self._watched_services:
            info = self._get_service_info(name)
            old = self._services.get(name)

            if old and old.status != info.status:
                alert = Alert(
                    severity=(
                        AlertSeverity.ERROR
                        if info.status == ServiceStatus.FAILED
                        else AlertSeverity.WARNING
                    ),
                    title=f"Service {name} status changed",
                    message=f"{name}: {old.status.value} → {info.status.value}",
                    source="service_monitor",
                )
                self._alerts.append(alert)
                logger.warning(f"Alert: {alert.title} — {alert.message}")

            self._services[name] = info

    def _get_service_info(self, name: str) -> ServiceInfo:
        """Detect service type and get its status."""
        # Try systemd first
        status = self._check_systemd(name)
        if status is not None:
            return status

        # Try Docker
        status = self._check_docker(name)
        if status is not None:
            return status

        # Try as process
        return self._check_process(name)

    def _check_systemd(self, name: str) -> ServiceInfo | None:
        """Check a systemd service."""
        import subprocess

        try:
            result = subprocess.run(
                ["systemctl", "is-active", name],
                capture_output=True, text=True, timeout=5,
            )
            active = result.stdout.strip()

            result2 = subprocess.run(
                ["systemctl", "show", name, "--property=MainPID,ActiveEnterTimestamp"],
                capture_output=True, text=True, timeout=5,
            )
            props = {}
            for line in result2.stdout.strip().split("\n"):
                if "=" in line:
                    k, v = line.split("=", 1)
                    props[k] = v

            status_map = {
                "active": ServiceStatus.ACTIVE,
                "inactive": ServiceStatus.INACTIVE,
                "failed": ServiceStatus.FAILED,
                "activating": ServiceStatus.ACTIVATING,
                "deactivating": ServiceStatus.DEACTIVATING,
            }

            return ServiceInfo(
                name=name,
                type="systemd",
                status=status_map.get(active, ServiceStatus.UNKNOWN),
                pid=int(props.get("MainPID", 0)) or None,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _check_docker(self, name: str) -> ServiceInfo | None:
        """Check a Docker container."""
        try:
            import docker
            client = docker.from_env()
            container = client.containers.get(name)
            health = container.attrs["State"].get("Health", {}).get("Status")

            status_map = {
                "running": ServiceStatus.ACTIVE,
                "exited": ServiceStatus.INACTIVE,
                "restarting": ServiceStatus.ACTIVATING,
            }

            return ServiceInfo(
                name=name,
                type="docker",
                status=status_map.get(container.status, ServiceStatus.UNKNOWN),
                health=health,
                pid=container.attrs["State"].get("Pid"),
                metadata={
                    "image": container.image.tags[0] if container.image.tags else "",
                    "created": container.attrs["Created"],
                },
            )
        except Exception:
            return None

    def _check_process(self, name: str) -> ServiceInfo:
        """Check if a process is running by name."""
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] == name or (
                    proc.info["cmdline"]
                    and any(name in arg for arg in proc.info["cmdline"])
                ):
                    mem = proc.memory_info()
                    return ServiceInfo(
                        name=name,
                        type="process",
                        status=ServiceStatus.ACTIVE,
                        pid=proc.pid,
                        memory_mb=round(mem.rss / (1024 * 1024), 1),
                        cpu_percent=proc.cpu_percent(interval=0.1),
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return ServiceInfo(
            name=name, type="process", status=ServiceStatus.INACTIVE
        )

    def _check_resources(self):
        """Check system resource thresholds."""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        if mem.percent > 90:
            self._alerts.append(Alert(
                severity=AlertSeverity.CRITICAL,
                title="Memory usage critical",
                message=f"Memory at {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)",
                source="resource_monitor",
            ))

        if disk.percent > 90:
            self._alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                title="Disk usage high",
                message=f"Disk at {disk.percent}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)",
                source="resource_monitor",
            ))

    def get_services(self) -> list[ServiceInfo]:
        return list(self._services.values())

    def get_alerts(self, unresolved_only: bool = True) -> list[Alert]:
        alerts = self._alerts
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        return alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
