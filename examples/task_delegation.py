#!/usr/bin/env python3
"""Example 3: Remote command execution and task delegation."""

import httpx
import time

SERVER_URL = "http://100.109.105.19:8000"


def main():
    client = httpx.Client(timeout=30)

    # 1. Run a simple command
    print("Executing: uptime")
    resp = client.post(
        f"{SERVER_URL}/api/v1/command",
        json={
            "command": "uptime",
            "args": [],
            "timeout_seconds": 10,
        },
    )
    result = resp.json()
    print(f"  Exit code: {result['exit_code']}")
    print(f"  Output: {result['stdout']}")

    # 2. Run a command with working directory
    print("\nExecuting: ls -la /home/serpico")
    resp = client.post(
        f"{SERVER_URL}/api/v1/command",
        json={
            "command": "ls",
            "args": ["-la", "/home/serpico"],
            "timeout_seconds": 10,
        },
    )
    result = resp.json()
    print(f"  Exit code: {result['exit_code']}")
    print(f"  Output:\n{result['stdout']}")

    # 3. Create and run a task
    print("\nCreating a task...")
    task_data = {
        "id": f"task-{int(time.time())}",
        "title": "Check disk usage",
        "command": "df -h",
        "timeout_seconds": 15,
        "priority": "high",
    }
    resp = client.post(f"{SERVER_URL}/api/v1/tasks", json=task_data)
    task = resp.json()
    print(f"  Task created: {task['id']} — {task['title']}")

    # Execute the task
    resp = client.post(f"{SERVER_URL}/api/v1/tasks/{task['id']}/run")
    result = resp.json()
    print(f"  Status: {result['status']}")
    print(f"  Result:\n{result.get('result', '')}")


if __name__ == "__main__":
    main()
