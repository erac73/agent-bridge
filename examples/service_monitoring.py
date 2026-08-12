#!/usr/bin/env python3
"""Example 2: Service monitoring and management."""

import httpx

SERVER_URL = "http://100.109.105.19:8000"


def main():
    client = httpx.Client(timeout=10)

    # 1. List all services
    resp = client.get(f"{SERVER_URL}/api/v1/services")
    services = resp.json()

    print("Monitored Services:")
    print(f"{'Name':<25} {'Type':<12} {'Status':<12} {'PID':<8}")
    print("-" * 60)
    for svc in services:
        pid = svc.get("pid") or ""
        print(f"{svc['name']:<25} {svc['type']:<12} {svc['status']:<12} {str(pid):<8}")

    # 2. Watch a new service
    print(f"\nWatching 'docker'...")
    client.post(f"{SERVER_URL}/api/v1/services/docker/watch")

    # 3. Restart a service
    # client.post(f"{SERVER_URL}/api/v1/services/nginx/restart")

    # 4. Get alerts
    resp = client.get(f"{SERVER_URL}/api/v1/alerts")
    alerts = resp.json()
    print(f"\nActive Alerts ({len(alerts)}):")
    for alert in alerts:
        print(f"  [{alert['severity'].upper()}] {alert['title']}: {alert['message']}")


if __name__ == "__main__":
    main()
