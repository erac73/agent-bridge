#!/usr/bin/env python3
"""Example 4: Multi-server management."""

import httpx
import concurrent.futures

SERVERS = [
    {"name": "mypi", "url": "http://100.109.105.19:8000"},
]


def check_server(server: dict) -> dict:
    """Check health of a single server."""
    client = httpx.Client(timeout=5)
    try:
        resp = client.get(f"{server['url']}/health/live", timeout=5)
        online = resp.status_code == 200
    except Exception:
        online = False

    if online:
        try:
            status = client.get(f"{server['url']}/api/v1/status").json()
            return {**server, "online": True, "status": status}
        except Exception:
            pass

    return {**server, "online": False, "status": None}


def main():
    print("Checking servers...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_server, SERVERS))

    for srv in results:
        status = "[ONLINE]" if srv["online"] else "[OFFLINE]"
        print(f"{srv['name']} ({srv['url']}): {status}")

        if srv["status"]:
            s = srv["status"]
            print(f"  CPU: {s['cpu_percent']}% | Mem: {s['memory_percent']}% | Disk: {s['disk_percent']}%")
            print(f"  Services: {len(s.get('services', []))}")
        print()

    # Execute command on all servers simultaneously
    print("\nExecuting 'uptime' on all servers...")
    client = httpx.Client(timeout=10)

    def run_on_server(srv):
        try:
            resp = client.post(
                f"{srv['url']}/api/v1/command",
                json={"command": "uptime", "args": [], "timeout_seconds": 5},
            )
            return srv["name"], resp.json()
        except Exception as e:
            return srv["name"], {"error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for name, result in executor.map(lambda srv: run_on_server(srv), SERVERS):
            if "error" in result:
                print(f"  {name}: {result['error']}")
            else:
                print(f"  {name}: {result['stdout'].strip()}")


if __name__ == "__main__":
    main()
