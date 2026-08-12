<p align="center">
  <img src="docs/logo.svg" width="220" alt="Agent Bridge"/>
</p>

<h1 align="center">Agent Bridge</h1>

<p align="center">
  <strong>PC to Server communication system for remote monitoring and task execution</strong><br/>
  <em>Your Raspberry Pi at your fingertips — from anywhere in the world.</em>
</p>

<p align="center">
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/java-11+-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/fastapi-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/docker-24.0-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/></a>
  <a href="https://github.com/erac73/agent-bridge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/></a>
</p>

---

<br/>

## What is Agent Bridge?

Agent Bridge is a **PC-to-Server communication system** that lets you monitor, control, and execute tasks on remote servers (Raspberry Pi, VPS, NAS) from your local computer — all through a REST API, a CLI, or a Java client.

<br/>

### The Problem

```
Without Agent Bridge:
  1. SSH into your Pi
  2. Run commands manually
  3. Copy-paste output back
  4. No monitoring
  5. No dashboard
  6. Repeat for every server
```

### The Solution

```
With Agent Bridge:
  1. agent-bridge server status mypi     # One command
  2. agent-bridge dashboard mypi         # Live view
  3. agent-bridge task run mypi "cmd"    # Remote execution
  4. All servers managed from one place
```

<br/>

---

<br/>

## How Communication Works

### The Big Picture

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

### Step-by-Step Data Flow

```
1. You type:  agent-bridge task run mypi "docker ps"

2. CLI (Typer) parses the command:
   server = "mypi"
   command = "docker"
   args = ["ps"]

3. Task Manager looks up server URL:
   mypi -> http://100.109.105.19:8000

4. HTTP Client (httpx) sends request:
   POST http://100.109.105.19:8000/api/v1/command
   Body: {"command": "docker", "args": ["ps"]}

5. Network carries the request:
   Tailscale (WireGuard) / Cloudflare (TLS) / SSH / LAN

6. Server Agent (FastAPI) receives and routes:
   /api/v1/command -> api.execute_command()

7. Server executes:
   subprocess.run(["docker", "ps"], capture_output=True)

8. Docker daemon runs the command, returns output

9. Server packages response as JSON:
   {"exit_code": 0, "stdout": "NAME STATUS\nnginx Up\n..."}

10. Response travels back to PC

11. PC Agent displays formatted output
```

### Network Options

<table>
<tr>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/network.png" alt="net"/> Method</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/settings.png" alt="setup"/> How It Works</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/speed.png" alt="speed"/> Latency</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/shield.png" alt="security"/> Security</th>
</tr>
<tr>
<td><strong>Tailscale</strong></td>
<td>WireGuard VPN tunnel via Tailscale relay</td>
<td>~1-5ms</td>
<td>Machine-level encryption</td>
</tr>
<tr>
<td><strong>Cloudflare Tunnel</strong></td>
<td>Outbound connection to Cloudflare edge</td>
<td>~10-50ms</td>
<td>TLS 1.3 + WAF</td>
</tr>
<tr>
<td><strong>SSH Tunnel</strong></td>
<td>Local port forwarding over SSH</td>
<td>~1-5ms</td>
<td>SSH encryption</td>
</tr>
<tr>
<td><strong>Direct LAN</strong></td>
<td>Raw TCP/IP on local network</td>
<td>~0.1ms</td>
<td>None (trusted only)</td>
</tr>
</table>

<br/>

---

<br/>

## Tools and Technologies

### Core Stack

<table>
<tr>
<td align="center">
  <img src="https://img.icons8.com/color/48/python.png" width="48"/><br/>
  <strong>Python 3.11+</strong><br/>
  <sub>Type hints, asyncio, Pydantic</sub>
</td>
<td align="center">
  <img src="https://img.icons8.com/color/48/fastapi.png" width="48"/><br/>
  <strong>FastAPI</strong><br/>
  <sub>Async REST API framework</sub>
</td>
<td align="center">
  <img src="https://img.icons8.com/color/48/java-coffee-cup-logo.png" width="48"/><br/>
  <strong>Java 11+</strong><br/>
  <sub>HttpClient + Jackson</sub>
</td>
<td align="center">
  <img src="https://img.icons8.com/color/48/docker.png" width="48"/><br/>
  <strong>Docker</strong><br/>
  <sub>Container management</sub>
</td>
</tr>
</table>

### Libraries Explained

<table>
<tr><th>Library</th><th>Used In</th><th>What It Does</th></tr>
<tr>
<td><strong>FastAPI</strong></td>
<td>Server Agent</td>
<td>Creates the REST API. Routes <code>GET /api/v1/status</code> to the correct function, validates inputs, returns JSON.</td>
</tr>
<tr>
<td><strong>Pydantic</strong></td>
<td>Shared Module</td>
<td>Defines data models with type validation. Ensures <code>{"cpu_percent": 12.5}</code> is actually a float.</td>
</tr>
<tr>
<td><strong>psutil</strong></td>
<td>Server Agent</td>
<td>Reads system metrics: CPU, memory, disk, network, processes. The "eyes" of the server.</td>
</tr>
<tr>
<td><strong>Docker SDK</strong></td>
<td>Server Agent</td>
<td>Queries Docker daemon for container status, restarts, logs. Direct socket communication.</td>
</tr>
<tr>
<td><strong>httpx</strong></td>
<td>PC Agent</td>
<td>Sends HTTP requests from PC to Server. The "hands" of the client.</td>
</tr>
<tr>
<td><strong>Typer</strong></td>
<td>PC Agent</td>
<td>Builds the CLI. Parses <code>agent-bridge server status mypi</code> into function calls.</td>
</tr>
<tr>
<td><strong>Rich</strong></td>
<td>PC Agent</td>
<td>Renders tables, panels, live dashboards in the terminal.</td>
</tr>
<tr>
<td><strong>Uvicorn</strong></td>
<td>Server Agent</td>
<td>ASGI server running FastAPI. Handles async HTTP connections.</td>
</tr>
<tr>
<td><strong>python-jose</strong></td>
<td>Shared Module</td>
<td>JWT token creation/verification for API key authentication.</td>
</tr>
<tr>
<td><strong>Jackson</strong></td>
<td>Java Client</td>
<td>JSON serialization/deserialization for Java HTTP client.</td>
</tr>
<tr>
<td><strong>Tailscale</strong></td>
<td>Network</td>
<td>WireGuard VPN mesh. Stable IPs (100.x.x.x) across devices.</td>
</tr>
</table>

<br/>

---

<br/>

## Features

<table>
  <tr>
    <td width="50%" valign="top">

<h3><img src="https://img.icons8.com/ios-filled/20/00d4ff/system-status.png" alt="monitor"/> System Monitoring</h3>

- CPU, memory, disk, network usage
- Load average and uptime tracking
- Real-time metrics via REST API
- Threshold-based alerts

<h3><img src="https://img.icons8.com/ios-filled/20/7b2ff7/terminal.png" alt="command"/> Remote Commands</h3>

- Execute any shell command remotely
- Timeout control and working directory
- Environment variable support
- Real-time stdout/stderr streaming

    </td>
    <td width="50%" valign="top">

<h3><img src="https://img.icons8.com/ios-filled/20/ff0080/health-check.png" alt="watchdog"/> Service Watchdog</h3>

- Monitor <strong>systemd</strong> services
- Monitor <strong>Docker</strong> containers
- Monitor <strong>processes</strong> by name
- Auto-detect service type

<h3><img src="https://img.icons8.com/ios-filled/20/00e676/dashboard.png" alt="dashboard"/> Live Dashboard</h3>

- Rich-powered real-time view
- Color-coded status indicators
- Service health overview
- Alert notifications

    </td>
  </tr>
</table>

<br/>

---

<br/>

## What You Can Do

### System Monitoring

```
Agent: mypi (Raspberry Pi 5)
CPU:    12.5% (4 cores)
Memory: 2.1 / 7.64 GB (27.5%)
Disk:   23.8 / 27.0 GB (88.1%)
Load:   0.5 / 0.3 / 0.2
```

### Service Management

| Action | Command | What Happens |
|--------|---------|--------------|
| List services | `service list mypi` | Reads systemd + Docker status |
| Restart service | `service restart mypi nginx` | Runs `systemctl restart nginx` |
| Watch service | `service watch mypi docker` | Adds to monitoring loop |
| Stop service | `service stop mypi postgres` | Runs `systemctl stop postgres` |

### Remote Command Execution

```bash
agent-bridge task run mypi "df -h"              # Disk usage
agent-bridge task run mypi "docker ps"           # List containers
agent-bridge task run mypi "uptime"              # System uptime
agent-bridge task run mypi "journalctl -u nginx" # View logs
```

### Docker Container Management

```bash
agent-bridge task run mypi "docker ps -a"         # All containers
agent-bridge task run mypi "docker restart postgres"  # Restart
agent-bridge task run mypi "docker logs --tail 50"    # Logs
agent-bridge task run mypi "docker stats --no-stream" # Resources
```

### Multi-Server Management

```bash
agent-bridge server add home-pi http://100.109.105.19:8000
agent-bridge server add vps https://agent.myvps.com
agent-bridge server add nas http://192.168.1.100:8000
agent-bridge status  # Check all at once
```

### Alert System

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Memory usage | > 90% | CRITICAL |
| Disk usage | > 90% | WARNING |
| Service down | status change | ERROR |
| Service restarting | status change | WARNING |

<br/>

---

<br/>

## CLI Commands

<table>
<tr>
<th><img src="https://img.icons8.com/ios-filled/14/fff/command.png" alt="cmd"/> Command</th>
<th><img src="https://img.icons8.com/ios-filled/14/fff/info.png" alt="info"/> Description</th>
<th><img src="https://img.icons8.com/ios-filled/14/fff/code.png" alt="code"/> Example</th>
</tr>
<tr>
<td><code>server add</code></td>
<td>Register a new server</td>
<td><code>agent-bridge server add mypi http://100.109.105.19:8000</code></td>
</tr>
<tr>
<td><code>server list</code></td>
<td>List all registered servers</td>
<td><code>agent-bridge server list</code></td>
</tr>
<tr>
<td><code>server status</code></td>
<td>System metrics for a server</td>
<td><code>agent-bridge server status mypi</code></td>
</tr>
<tr>
<td><code>task run</code></td>
<td>Execute a command remotely</td>
<td><code>agent-bridge task run mypi "docker ps"</code></td>
</tr>
<tr>
<td><code>service list</code></td>
<td>Show monitored services</td>
<td><code>agent-bridge service list mypi</code></td>
</tr>
<tr>
<td><code>service restart</code></td>
<td>Restart a remote service</td>
<td><code>agent-bridge service restart mypi nginx</code></td>
</tr>
<tr>
<td><code>dashboard</code></td>
<td>Live monitoring dashboard</td>
<td><code>agent-bridge dashboard mypi</code></td>
</tr>
</table>

<br/>

---

<br/>

## Java Client

Full Java 11+ client included with Jackson for JSON serialization.

<h3><img src="https://img.icons8.com/ios-filled/16/ED8B00/java.png" alt="java"/> Usage</h3>

```java
import com.agentbridge.client.AgentClient;
import com.agentbridge.models.*;

AgentClient client = new AgentClient("http://100.109.105.19:8000");

// Health check
HealthStatus health = client.healthCheck();
System.out.println("Status: " + health.status);

// Server status
ServerStatus status = client.getServerStatus();
System.out.println("CPU: " + status.cpuPercent + "%");
System.out.println("Memory: " + status.memoryUsedGb + " / " + status.memoryTotalGb + " GB");

// Execute command
CommandResult result = client.executeCommand("docker", new String[]{"ps"}, 15);
System.out.println(result.stdout);

// List services
List<ServiceInfo> services = client.getServices();
for (ServiceInfo svc : services) {
    System.out.println(svc.name + ": " + svc.status);
}

// Restart a service
client.restartService("nginx");
```

<h3><img src="https://img.icons8.com/ios-filled/16/ED8B00/java.png" alt="java"/> Build and Run</h3>

```bash
cd examples/java
mvn compile exec:java -Dexec.mainClass="com.agentbridge.Main"
```

<br/>

---

<br/>

## Project Structure

```
agent-bridge/
+-- shared/                    [+] Shared library
|   +-- models.py              Pydantic data models
|   +-- protocol.py            Message protocol definitions
|   +-- crypto.py              mTLS and API key management
|
+-- server-agent/              [+] Server-side agent
|   +-- main.py                FastAPI entry point
|   +-- agent.py               Core logic
|   +-- api.py                 REST endpoints
|   +-- monitor.py             Service watchdog
|   +-- Dockerfile             Container build
|
+-- pc-agent/                  [+] PC-side agent
|   +-- main.py                CLI entry point
|   +-- cli.py                 Typer commands
|   +-- task_manager.py        Server registry
|   +-- monitor_dashboard.py   Rich live view
|   +-- Dockerfile             Container build
|
+-- examples/
|   +-- java/                  [+] Java client (Maven)
|   +-- basic_connection.py    Python example
|   +-- service_monitoring.py
|   +-- task_delegation.py
|   +-- multi_server.py
|
+-- deploy/                    [+] Deployment
|   +-- docker-compose.yml
|
+-- docs/                      [+] Documentation
|   +-- HOW_IT_WORKS.md        Deep dive explanation
|   +-- architecture.md
|   +-- protocol-spec.md
|   +-- security.md
|   +-- deployment.md
```

<br/>

---

<br/>

## Security

Agent Bridge supports **multiple layers** of security:

```
+----------------------------------------------+
|  Layer 1: Network Encryption                 |
|  -----------------------------------------   |
|  Tailscale (WireGuard) / Cloudflare (TLS 1.3)|
+----------------------------------------------+
|  Layer 2: Authentication                     |
|  -----------------------------------------   |
|  API Key (Bearer Token) / mTLS (Mutual TLS) |
+----------------------------------------------+
|  Layer 3: Authorization                      |
|  -----------------------------------------   |
|  Limited user / Sudo rules / Isolation       |
+----------------------------------------------+
```

<br/>

---

<br/>

## Docker Deployment

```bash
# Build and start the server agent
docker compose -f deploy/docker-compose.yml up -d

# Check logs
docker logs -f server-agent

# Stop
docker compose -f deploy/docker-compose.yml down
```

<br/>

---

<br/>

## API Endpoints

<details>
<summary><img src="https://img.icons8.com/ios-filled/14/00d4ff/system-status.png" alt="status"/> <strong>GET /api/v1/status</strong> — System Status</summary>

```json
{
  "hostname": "raspberrypi",
  "cpu_percent": 12.5,
  "memory_percent": 27.5,
  "disk_percent": 88.1,
  "load_avg_1": 0.5,
  "kernel_version": "6.12.96",
  "services": [...]
}
```

</details>

<details>
<summary><img src="https://img.icons8.com/ios-filled/14/7b2ff7/terminal.png" alt="cmd"/> <strong>POST /api/v1/command</strong> — Execute Command</summary>

```json
// Request
{ "command": "docker", "args": ["ps"], "timeout_seconds": 15 }

// Response
{ "exit_code": 0, "stdout": "...", "duration_seconds": 0.123 }
```

</details>

<details>
<summary><img src="https://img.icons8.com/ios-filled/14/ff0080/health-check.png" alt="svc"/> <strong>GET /api/v1/services</strong> — Monitored Services</summary>

```json
[
  { "name": "nginx", "type": "systemd", "status": "active", "pid": 1234 },
  { "name": "postgres", "type": "docker", "status": "active", "pid": 5678 }
]
```

</details>

<details>
<summary><img src="https://img.icons8.com/ios-filled/14/ffaa00/alert.png" alt="alert"/> <strong>GET /api/v1/alerts</strong> — Active Alerts</summary>

```json
[
  { "severity": "warning", "title": "Disk usage high", "message": "Disk at 92%" }
]
```

</details>

<br/>

---

<br/>

## Quick Start

<h3><img src="https://img.icons8.com/ios-filled/16/00d4ff/download.png" alt="install"/> Install</h3>

```bash
git clone https://github.com/erac73/agent-bridge.git
cd agent-bridge
pip install -r server-agent/requirements.txt
```

<h3><img src="https://img.icons8.com/ios-filled/16/7b2ff7/server.png" alt="server"/> Run Server (on your Pi)</h3>

```bash
cd server-agent
python main.py
```

<h3><img src="https://img.icons8.com/ios-filled/16/00e676/laptop.png" alt="pc"/> Run PC Agent (from your computer)</h3>

```bash
cd pc-agent
pip install -r requirements.txt
python main.py server add mypi http://100.109.105.19:8000
python main.py server status mypi
```

<br/>

---

<br/>

## Made with

<table>
<tr>
<td align="center"><img src="https://img.icons8.com/color/48/python.png" width="40"/><br/><sub>Python</sub></td>
<td align="center"><img src="https://img.icons8.com/color/48/java-coffee-cup-logo.png" width="40"/><br/><sub>Java 11+</sub></td>
<td align="center"><img src="https://img.icons8.com/ios/48/fastapi.png" width="40"/><br/><sub>FastAPI</sub></td>
<td align="center"><img src="https://img.icons8.com/color/48/docker.png" width="40"/><br/><sub>Docker</sub></td>
<td align="center"><img src="https://img.icons8.com/color/48/tailscale.png" width="40"/><br/><sub>Tailscale</sub></td>
</tr>
</table>

<br/>

---

<br/>

<p align="center">
  <sub>
    Built by <a href="https://github.com/erac73">erac73</a> |
    Licensed under <a href="LICENSE">MIT</a>
  </sub>
</p>
