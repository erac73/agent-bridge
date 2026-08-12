<h1 align="center">How It Works</h1>

<p align="center">
  A deep dive into how Agent Bridge achieves PC-to-Server communication,<br/>
  the tools involved, and the tasks you can accomplish.
</p>

---

<br/>

## Table of Contents

1. [Communication Overview](#communication-overview)
2. [The Two Agents](#the-two-agents)
3. [Transport Layer — How Data Travels](#transport-layer)
4. [Application Layer — The REST API](#application-layer)
5. [Security Layer — Authentication and Encryption](#security-layer)
6. [Tools and Technologies](#tools-and-technologies)
7. [Task Lifecycle](#task-lifecycle)
8. [What You Can Do](#what-you-can-do)
9. [Step-by-Step Example](#step-by-step-example)

<br/>

---

<br/>

## Communication Overview

Agent Bridge uses a **client-server architecture** where:

```
+------------------+                              +------------------+
|                  |      HTTP/HTTPS Request      |                  |
|    PC Agent      | ---------------------------> |   Server Agent   |
|    (Client)      |                              |   (FastAPI)      |
|                  | <--------------------------- |                  |
+------------------+      JSON Response           +------------------+
        |                                                 |
        |                                                 |
   Runs on your                                      Runs on your
   Windows/Mac/Linux                                 Raspberry Pi/VPS
```

The PC Agent sends **HTTP requests** to the Server Agent, which processes them and returns **JSON responses**. Both agents share the same **data models** (Pydantic) to ensure type-safe communication.

<br/>

---

<br/>

## The Two Agents

### PC Agent (Client)

| Component | Purpose |
|-----------|---------|
| `cli.py` | Typer-based command-line interface |
| `task_manager.py` | Server registry and HTTP client |
| `monitor_dashboard.py` | Rich live dashboard |

The PC Agent is a **thin client**. It does not process data locally — it sends requests to the server and displays results. Think of it as a **remote control** for your servers.

### Server Agent (Server)

| Component | Purpose |
|-----------|---------|
| `main.py` | FastAPI application entry point |
| `agent.py` | Core logic: task execution, heartbeat, identity |
| `api.py` | REST API endpoints (the "brain") |
| `monitor.py` | Background watchdog thread (systemd + Docker + process) |

The Server Agent is the **workhorse**. It runs on your server, monitors services, executes commands, and responds to PC Agent requests.

<br/>

---

<br/>

## Transport Layer

### How Data Travels from PC to Server

```
Step 1: PC Agent creates an HTTP request
        |
        v
Step 2: Request travels over the network
        |  - LAN: Direct TCP/IP (fastest)
        |  - Tailscale: WireGuard VPN tunnel
        |  - Cloudflare: TLS 1.3 encrypted tunnel
        |  - SSH: Encrypted SSH tunnel
        v
Step 3: Server Agent receives the request
        |
        v
Step 4: FastAPI parses the request and routes it
        |
        v
Step 5: Handler function processes the request
        |  - Reads system metrics (psutil)
        |  - Executes commands (subprocess)
        |  - Queries Docker (docker SDK)
        |  - Checks systemd (systemctl)
        v
Step 6: Response is serialized as JSON
        |
        v
Step 7: JSON response travels back to PC
        |
        v
Step 8: PC Agent parses JSON and displays results
```

### Network Options

| Option | How It Works | Latency | Security |
|--------|-------------|---------|----------|
| **Tailscale** | WireGuard UDP tunnel via Tailscale relay | ~1-5ms | Machine-level encryption |
| **Cloudflare Tunnel** | Outbound connection to Cloudflare edge | ~10-50ms | TLS 1.3 + Cloudflare WAF |
| **SSH Tunnel** | Local port forwarding over SSH | ~1-5ms | SSH encryption |
| **Direct LAN** | Raw TCP/IP on local network | ~0.1-1ms | None (trusted network) |

<br/>

---

<br/>

## Application Layer

### The REST API Protocol

All communication happens through **HTTP requests** with **JSON payloads**:

```
PC Agent                           Server Agent
    |                                    |
    |  GET /health/live                  |
    | ---------------------------------> |
    |                                    |
    |  <-- {"status": "alive"} --------- |
    |                                    |
    |  GET /api/v1/status                |
    | ---------------------------------> |
    |                                    |
    |  <-- {cpu_percent, memory, ...} -- |
    |                                    |
    |  POST /api/v1/command              |
    |  {"command": "docker", "args": ["ps"]} |
    | ---------------------------------> |
    |                                    |
    |  <-- {exit_code: 0, stdout: ...} - |
```

### Request/Response Format

**Request:**
```http
POST /api/v1/command HTTP/1.1
Host: 100.109.105.19:8000
Content-Type: application/json
Authorization: Bearer <api-key>

{
  "command": "docker",
  "args": ["ps", "--format", "table {{.Names}}\t{{.Status}}"],
  "timeout_seconds": 15
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "request_id": "req-abc123",
  "exit_code": 0,
  "stdout": "NAME      STATUS\npostgres  Up 2 hours\n...",
  "stderr": "",
  "started_at": "2026-08-11T12:00:00Z",
  "completed_at": "2026-08-11T12:00:01Z",
  "duration_seconds": 0.123
}
```

<br/>

---

<br/>

## Security Layer

### Authentication Flow

```
Step 1: PC Agent includes API key in request header
        |
        |  Authorization: Bearer ghp_xxxxxxxxxxxx
        v
Step 2: Server Agent validates the token
        |
        |  - Check against configured api_key
        |  - Reject if mismatched
        v
Step 3: If valid, process the request
        |
        v
Step 4: If invalid, return 401 Unauthorized
```

### mTLS (Mutual TLS) Flow

```
Step 1: PC connects to Server
        |
        v
Step 2: Server presents its certificate
        |
        v
Step 3: PC presents its certificate
        |
        v
Step 4: Both verify each other's certificate
        |  - Check against shared CA
        |  - Verify expiry
        |  - Check revocation
        v
Step 5: Encrypted channel established
```

<br/>

---

<br/>

## Tools and Technologies

### Core Stack

<table>
<tr>
<td align="center">
  <img src="https://img.icons8.com/color/48/fastapi.png" width="48"/><br/>
  <strong>FastAPI</strong><br/>
  <sub>Async REST API framework</sub><br/>
  <sub>Auto-generates OpenAPI docs</sub><br/>
  <sub>High performance (uvicorn)</sub>
</td>
<td align="center">
  <img src="https://img.icons8.com/color/48/python.png" width="48"/><br/>
  <strong>Python 3.11+</strong><br/>
  <sub>Type hints throughout</sub><br/>
  <sub>Pydantic for validation</sub><br/>
  <sub>asyncio support</sub>
</td>
<td align="center">
  <img src="https://img.icons8.com/color/48/java-coffee-cup-logo.png" width="48"/><br/>
  <strong>Java 11+</strong><br/>
  <sub>HttpClient for REST</sub><br/>
  <sub>Jackson for JSON</sub><br/>
  <sub>Maven for builds</sub>
</td>
</tr>
</table>

### Libraries Explained

<table>
<tr><th>Library</th><th>Used In</th><th>What It Does</th></tr>
<tr>
<td><strong>FastAPI</strong></td>
<td>Server Agent</td>
<td>Creates the REST API. When you call <code>GET /api/v1/status</code>, FastAPI routes it to the correct function, validates inputs, and returns JSON.</td>
</tr>
<tr>
<td><strong>Pydantic</strong></td>
<td>Shared Module</td>
<td>Defines data models with type validation. When the server returns <code>{"cpu_percent": 12.5}</code>, Pydantic ensures it's actually a float, not a string.</td>
</tr>
<tr>
<td><strong>psutil</strong></td>
<td>Server Agent</td>
<td>Reads system metrics: CPU usage, memory, disk, network, processes. The "eyes" of the server agent.</td>
</tr>
<tr>
<td><strong>Docker SDK</strong></td>
<td>Server Agent</td>
<td>Queries Docker daemon for container status, restarts containers, reads logs. Direct communication with the Docker socket.</td>
</tr>
<tr>
<td><strong>httpx</strong></td>
<td>PC Agent</td>
<td>Sends HTTP requests from PC to Server. The "hands" of the PC agent — it reaches out to the server.</td>
</tr>
<tr>
<td><strong>Typer</strong></td>
<td>PC Agent</td>
<td>Builds the CLI interface. When you type <code>agent-bridge server status mypi</code>, Typer parses the command and calls the right function.</td>
</tr>
<tr>
<td><strong>Rich</strong></td>
<td>PC Agent</td>
<td>Renders beautiful terminal output: tables, panels, live dashboards. Makes the CLI visually appealing.</td>
</tr>
<tr>
<td><strong>Uvicorn</strong></td>
<td>Server Agent</td>
<td>ASGI server that runs FastAPI. Handles async HTTP connections efficiently.</td>
</tr>
<tr>
<td><strong>python-jose</strong></td>
<td>Shared Module</td>
<td>JWT token creation and verification for API key authentication.</td>
</tr>
<tr>
<td><strong>Tailscale</strong></td>
<td>Network</td>
<td>Creates a WireGuard VPN mesh. Devices get stable IPs (100.x.x.x) and can communicate securely anywhere.</td>
</tr>
</table>

### How Each Tool Contributes

```
PC Agent                          Server Agent
    |                                    |
    |  [Typer] parses CLI command        |
    |        |                           |
    |        v                           |
    |  [httpx] sends HTTP request       |
    |        |                           |
    |  ~~~ network (Tailscale) ~~~>     |
    |                                    |
    |                  [FastAPI] routes request
    |                        |           |
    |                        v           |
    |              [agent.py] processes  |
    |                        |           |
    |            +-----------+-----------+
    |            |           |           |
    |            v           v           v
    |         [psutil]  [Docker]  [subprocess]
    |         system    container  shell
    |         metrics   status     commands
    |            |           |           |
    |            +-----------+-----------+
    |                        |
    |  <~~~ network ~~~~    |
    |                        |
    |  [Pydantic] validates response
    |        |               |
    |        v               |
    |  [Rich] renders output
```

<br/>

---

<br/>

## Task Lifecycle

### How a Remote Command Executes

```
1. User types:  agent-bridge task run mypi "docker ps -a"

2. CLI parses:  command="docker", args=["ps", "-a"]

3. PC Agent sends POST request:
   POST /api/v1/command
   {"command": "docker", "args": ["ps", "-a"], "timeout_seconds": 60}

4. Server receives and creates a subprocess:
   subprocess.run(["docker", "ps", "-a"], capture_output=True, timeout=60)

5. Docker daemon executes the command

6. Output captured:
   stdout="CONTAINER ID   IMAGE   STATUS   NAMES\n..."
   exit_code=0

7. Server returns JSON response

8. PC Agent displays:
   Exit Code: 0
   Output:
   CONTAINER ID   IMAGE   STATUS   NAMES
   abc123         nginx   Up 2h    web
   def456         pg17    Up 3h    postgres
```

### Task States

```
  pending  ---->  assigned  ---->  running  ---->  completed
                      |                |
                      |                +---->  failed
                      |
                      +---->  cancelled
                      |
                      +---->  timeout
```

<br/>

---

<br/>

## What You Can Do

### 1. System Monitoring

```
Agent: mypi (Raspberry Pi 5)
CPU:    12.5% (4 cores)
Memory: 2.1 / 7.64 GB (27.5%)
Disk:   23.8 / 27.0 GB (88.1%)
Load:   0.5 / 0.3 / 0.2
```

### 2. Service Management

| Action | Command | What Happens |
|--------|---------|--------------|
| List services | `service list mypi` | Reads systemd + Docker status |
| Restart service | `service restart mypi nginx` | Runs `systemctl restart nginx` |
| Watch service | `service watch mypi docker` | Adds to monitoring loop |
| Stop service | `service stop mypi postgres` | Runs `systemctl stop postgres` |

### 3. Remote Command Execution

```bash
# Check disk usage
agent-bridge task run mypi "df -h"

# List running containers
agent-bridge task run mypi "docker ps"

# Check system uptime
agent-bridge task run mypi "uptime"

# View logs
agent-bridge task run mypi "journalctl -u nginx --since 1 hour ago"

# Update packages
agent-bridge task run mypi "sudo apt update && sudo apt upgrade -y"
```

### 4. Docker Container Management

```bash
# List all containers
agent-bridge task run mypi "docker ps -a"

# Restart a container
agent-bridge task run mypi "docker restart postgres"

# View container logs
agent-bridge task run mypi "docker logs --tail 50 postgres"

# Check container resources
agent-bridge task run mypi "docker stats --no-stream"
```

### 5. Live Dashboard

```
+------------------------------------------------------------------+
|           Agent Bridge Dashboard — raspberrypi                    |
+------------------------------------------------------------------+
| System                    | Services                              |
| ------------------------- | ------------------------------------- |
| CPU:     12.5%            | nginx        active    systemd   1234 |
| Memory:  2.1/7.6 GB       | postgres     active    docker    5678 |
| Disk:    23.8/27 GB       | docker       active    systemd   9012 |
| Network: 1.2GB 5.8GB      | ssh          active    systemd   2345 |
| Load:    0.5 / 0.3 / 0.2  | server-agent active    docker    3456 |
+------------------------------------------------------------------+
| Alerts                                                            |
| No active alerts                                                  |
+------------------------------------------------------------------+
```

### 6. Alert System

The server agent continuously monitors:

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Memory usage | > 90% | CRITICAL |
| Disk usage | > 90% | WARNING |
| Service down | status change | ERROR |
| Service restarting | status change | WARNING |

### 7. Multi-Server Management

```
+-----------+     +-----------+     +-----------+
|  Pi 5     |     |  VPS      |     |  NAS      |
|  :8000    |     |  :8000    |     |  :8000    |
+-----------+     +-----------+     +-----------+
      ^                 ^                 ^
      |                 |                 |
      +--------+--------+--------+--------+
               |
        +--------------+
        |   PC Agent   |
        |  (manages)   |
        +--------------+
```

<br/>

---

<br/>

## Step-by-Step Example

### Scenario: Monitor your Raspberry Pi from your Windows PC

**Prerequisites:**
- Raspberry Pi running `server-agent` on port 8000
- Windows PC with `pc-agent` installed
- Tailscale connected on both devices

**Step 1: Add the server**
```bash
python main.py server add mypi http://100.109.105.19:8000
```

**Step 2: Check status**
```bash
python main.py server status mypi
```
Output:
```
┌─────────────────────────────────────┐
│          raspberrypi                │
├─────────────────────────────────────┤
│ CPU:     12.5% (4 cores)           │
│ Load:    0.5 / 0.3 / 0.2          │
│ Memory:  2.1/7.64 GB (27.5%)      │
│ Disk:    23.8/27 GB (88.1%)       │
│ Network: ↑1.2GB  ↓5.8GB           │
│ Kernel:  6.12.96                   │
└─────────────────────────────────────┘
```

**Step 3: List services**
```bash
python main.py service list mypi
```
Output:
```
Name          Type       Status     PID
------------------------------------------------
ssh           systemd    active     456
docker        systemd    active     789
nginx         docker     active     1234
postgres      docker     active     5678
```

**Step 4: Run a command**
```bash
python main.py task run mypi "docker ps --format table {{.Names}}\t{{.Status}}"
```
Output:
```
Docker Command
Exit code: 0
NAME        STATUS
nginx       Up 2 hours
postgres    Up 3 hours
redis       Up 1 hour
```

**Step 5: Launch live dashboard**
```bash
python main.py dashboard mypi
```

This shows a real-time updating view of your server's health, services, and alerts — refreshed every 5 seconds.

<br/>

---

<br/>

## Summary

| Layer | Technology | Role |
|-------|-----------|------|
| **CLI** | Typer + Rich | Parse commands, render output |
| **HTTP Client** | httpx (Python) / HttpClient (Java) | Send requests to server |
| **Network** | Tailscale / Cloudflare / SSH / LAN | Transport data securely |
| **REST API** | FastAPI + uvicorn | Receive and route requests |
| **Monitoring** | psutil + Docker SDK + systemctl | Read system state |
| **Task Execution** | subprocess (Python) / ProcessBuilder (Java) | Run commands on server |
| **Data Validation** | Pydantic (Python) / Jackson (Java) | Ensure type-safe communication |
| **Authentication** | API Key / mTLS | Secure access |

The beauty of Agent Bridge is that **all this complexity is hidden** behind simple CLI commands:

```bash
agent-bridge server status mypi     # Instead of: SSH in, run top, parse output
agent-bridge task run mypi "docker ps"  # Instead of: SSH in, run command, copy output
agent-bridge dashboard mypi         # Instead of: SSH in, install htop, monitor
```

**One command. Full control. From anywhere.**
