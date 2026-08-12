"""REST API — Endpoints for PC agent communication."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agent import ServerAgent
from monitor import ServiceMonitor
from shared.models import (
    Alert,
    CommandRequest,
    CommandResponse,
    ServiceInfo,
    ServerStatus,
    Task,
    TaskStatus,
)
from shared.protocol import AgentProtocol

import psutil
import platform
import subprocess


def create_router(agent: ServerAgent, monitor: ServiceMonitor) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["agent"])

    # ── Agent Info ──────────────────────────────────────────────────

    @router.get("/agent")
    async def get_agent_info():
        return agent.get_info()

    @router.get("/agent/heartbeat")
    async def get_heartbeat():
        return agent.get_heartbeat()

    # ── Server Status ───────────────────────────────────────────────

    @router.get("/status")
    async def get_server_status():
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        load = psutil.getloadavg()
        freq = psutil.cpu_freq()

        return ServerStatus(
            hostname=platform.node(),
            cpu_percent=psutil.cpu_percent(interval=0.5),
            cpu_count=psutil.cpu_count(logical=True),
            load_avg_1=load[0],
            load_avg_5=load[1],
            load_avg_15=load[2],
            memory_total_gb=round(mem.total / (1024**3), 2),
            memory_used_gb=round(mem.used / (1024**3), 2),
            memory_percent=mem.percent,
            disk_total_gb=round(disk.total / (1024**3), 2),
            disk_used_gb=round(disk.used / (1024**3), 2),
            disk_percent=disk.percent,
            net_sent_gb=round(net.bytes_sent / (1024**3), 3),
            net_recv_gb=round(net.bytes_recv / (1024**3), 3),
            uptime_seconds=psutil.boot_time(),
            kernel_version=platform.release(),
            services=monitor.get_services(),
        )

    # ── Services ────────────────────────────────────────────────────

    @router.get("/services")
    async def list_services():
        return monitor.get_services()

    @router.get("/services/{name}")
    async def get_service(name: str):
        for svc in monitor.get_services():
            if svc.name == name:
                return svc
        raise HTTPException(status_code=404, detail=f"Service '{name}' not found")

    @router.post("/services/{name}/watch")
    async def watch_service(name: str):
        monitor.watch_service(name)
        return {"message": f"Now watching '{name}'"}

    @router.post("/services/{name}/restart")
    async def restart_service(name: str):
        result = subprocess.run(
            ["sudo", "systemctl", "restart", name],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return {"message": f"Service '{name}' restarted"}

    @router.post("/services/{name}/stop")
    async def stop_service(name: str):
        result = subprocess.run(
            ["sudo", "systemctl", "stop", name],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return {"message": f"Service '{name}' stopped"}

    @router.post("/services/{name}/start")
    async def start_service(name: str):
        result = subprocess.run(
            ["sudo", "systemctl", "start", name],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return {"message": f"Service '{name}' started"}

    # ── Tasks ───────────────────────────────────────────────────────

    @router.get("/tasks")
    async def list_tasks(status: str | None = None):
        task_status = TaskStatus(status) if status else None
        return agent.list_tasks(status=task_status)

    @router.get("/tasks/{task_id}")
    async def get_task(task_id: str):
        task = agent.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @router.post("/tasks")
    async def create_task(task: Task):
        assigned = agent.assign_task(task)
        return assigned

    @router.post("/tasks/{task_id}/run")
    async def run_task(task_id: str):
        task = agent.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return await agent.run_task(task)

    # ── Commands ────────────────────────────────────────────────────

    @router.post("/command")
    async def execute_command(req: CommandRequest):
        return await agent.execute_command(req)

    # ── Alerts ──────────────────────────────────────────────────────

    @router.get("/alerts")
    async def list_alerts():
        return monitor.get_alerts()

    @router.post("/alerts/{alert_id}/ack")
    async def acknowledge_alert(alert_id: str):
        if not monitor.acknowledge_alert(alert_id):
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": f"Alert '{alert_id}' acknowledged"}

    return router
