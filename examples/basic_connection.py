#!/usr/bin/env python3
"""Example 1: Basic connection to a server agent."""

import httpx

SERVER_URL = "http://100.109.105.19:8000"


def main():
    client = httpx.Client(timeout=10)

    print(f"Connecting to {SERVER_URL}...")

    # 1. Health check
    resp = client.get(f"{SERVER_URL}/health/live")
    print(f"Health: {resp.json()}")

    # 2. Get agent info
    resp = client.get(f"{SERVER_URL}/api/v1/agent")
    info = resp.json()
    print(f"\nAgent: {info['agent_id']}")
    print(f"Hostname: {info['hostname']}")
    print(f"Type: {info['agent_type']}")
    print(f"Capabilities: {', '.join(info['capabilities'])}")

    # 3. Get system status
    resp = client.get(f"{SERVER_URL}/api/v1/status")
    status = resp.json()
    print(f"\nSystem Status — {status['hostname']}:")
    print(f"  CPU: {status['cpu_percent']}%")
    print(f"  Memory: {status['memory_used_gb']}/{status['memory_total_gb']} GB ({status['memory_percent']}%)")
    print(f"  Disk: {status['disk_used_gb']}/{status['disk_total_gb']} GB ({status['disk_percent']}%)")

    # 4. List services
    resp = client.get(f"{SERVER_URL}/api/v1/services")
    services = resp.json()
    print(f"\nWatched Services ({len(services)}):")
    for svc in services:
        print(f"  {svc['name']}: {svc['status']} ({svc['type']})")


if __name__ == "__main__":
    main()
