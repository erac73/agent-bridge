"""Server Agent — Core agent logic."""

from __future__ import annotations

import asyncio
import logging
import platform
import time
from datetime import datetime, timezone

import httpx
import psutil

from shared.models import (
    AgentInfo,
    CommandRequest,
    CommandResponse,
    Heartbeat,
    Task,
    TaskStatus,
)
from shared.protocol import AgentProtocol, AgentMessage, MessageType

logger = logging.getLogger("server-agent")


class ServerAgent:
    """Manages communication with the PC agent and task execution."""

    def __init__(self):
        self.agent_id = f"server-{platform.node()}"
        self.hostname = platform.node()
        self.version = "1.0.0"
        self._ready = False
        self._running = False
        self._pc_url: str = ""
        self._api_key: str = ""
        self._tasks: dict[str, Task] = {}
        self._http: httpx.AsyncClient | None = None

    @property
    def is_ready(self) -> bool:
        return self._ready

    async def start(self):
        """Initialize the agent."""
        self._http = httpx.AsyncClient(timeout=30)
        self._running = True
        self._ready = True
        logger.info(f"Server agent started: {self.agent_id}")

    async def stop(self):
        """Shutdown the agent."""
        self._running = False
        self._ready = False
        if self._http:
            await self._http.aclose()
        logger.info("Server agent stopped")

    def get_info(self) -> AgentInfo:
        """Return agent identity information."""
        return AgentInfo(
            agent_id=self.agent_id,
            hostname=self.hostname,
            agent_type="server",
            version=self.version,
            capabilities=[
                "service_management",
                "command_execution",
                "system_monitoring",
                "log_collection",
            ],
        )

    def get_heartbeat(self) -> Heartbeat:
        """Generate a heartbeat message."""
        pending = sum(
            1 for t in self._tasks.values()
            if t.status in (TaskStatus.PENDING, TaskStatus.ASSIGNED)
        )
        active = sum(
            1 for t in self._tasks.values()
            if t.status == TaskStatus.RUNNING
        )
        return Heartbeat(
            agent_id=self.agent_id,
            active_tasks=active,
            pending_tasks=pending,
            metrics={
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
            },
        )

    async def execute_command(self, req: CommandRequest) -> CommandResponse:
        """Execute a shell command and return the result."""
        import subprocess

        start = time.monotonic()
        logger.info(f"Executing command: {req.command} {' '.join(req.args)}")

        try:
            proc = subprocess.run(
                [req.command] + req.args,
                capture_output=True,
                text=True,
                timeout=req.timeout_seconds,
                cwd=req.working_dir,
                env={**__import__("os").environ, **req.env},
            )
            duration = time.monotonic() - start

            return CommandResponse(
                request_id=req.request_id,
                exit_code=proc.returncode,
                stdout=proc.stdout[:50000],  # Limit output
                stderr=proc.stderr[:10000],
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                duration_seconds=round(duration, 3),
            )
        except subprocess.TimeoutExpired:
            return CommandResponse(
                request_id=req.request_id,
                exit_code=-1,
                stderr=f"Command timed out after {req.timeout_seconds}s",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                duration_seconds=req.timeout_seconds,
            )
        except Exception as e:
            return CommandResponse(
                request_id=req.request_id,
                exit_code=-1,
                stderr=str(e),
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )

    def assign_task(self, task: Task) -> Task:
        """Accept a task assignment."""
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = self.agent_id
        self._tasks[task.id] = task
        logger.info(f"Task assigned: {task.id} — {task.title}")
        return task

    async def run_task(self, task: Task) -> Task:
        """Execute an assigned task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)

        if task.command:
            req = CommandRequest(
                command=task.command.split()[0],
                args=task.command.split()[1:],
                timeout_seconds=task.timeout_seconds,
            )
            result = await self.execute_command(req)
            task.exit_code = result.exit_code
            task.result = result.stdout
            task.error = result.stderr if result.exit_code != 0 else None
            task.status = (
                TaskStatus.COMPLETED if result.exit_code == 0 else TaskStatus.FAILED
            )
        else:
            task.result = "No command specified"
            task.status = TaskStatus.COMPLETED

        task.completed_at = datetime.now(timezone.utc)
        self._tasks[task.id] = task
        logger.info(f"Task {task.id} finished: {task.status.value}")
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_tasks(self, status: TaskStatus | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
