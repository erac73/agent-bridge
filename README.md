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
  <a href="https://github.com/erac73/agent-bridge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/></a>
</p>

---

<br/>

## What is this?

```
    +--------------+                            +--------------+
    |              |   -- TCP / HTTPS -->       |              |
    |   PC Agent   |                            | Server Agent |
    |   (CLI)      |   <-- JSON / REST --       |   (FastAPI)  |
    |              |                            |              |
    +--------------+                            +--------------+
          |                                           |
          |    +---------------------------------+    |
          |    |   Shared: Models / Protocol / mTLS   |
          |    +---------------------------------+    |
          |                                           |
    Monitor services                            Execute commands
    Run remote tasks                            Watch system health
    Live dashboard                              Generate alerts
```

Agent Bridge lets you **monitor**, **control**, and **execute tasks** on your remote servers (Raspberry Pi, VPS, NAS) from your PC — all through a clean REST API, a beautiful CLI, or a Java client.

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

<h3><img src="https://img.icons8.com/ios-filled/16/ED8B00/java.png" alt="java"/> Maven</h3>

```xml
<dependency>
    <groupId>com.agentbridge</groupId>
    <artifactId>agent-bridge-java-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

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

<h3><img src="https://img.icons8.com/ios-filled/16/ED8B00/java.png" alt="java"/> Available Models</h3>

<table>
<tr><th>Model</th><th>Description</th></tr>
<tr><td><code>AgentInfo</code></td><td>Agent identity and capabilities</td></tr>
<tr><td><code>ServerStatus</code></td><td>CPU, memory, disk, network metrics</td></tr>
<tr><td><code>ServiceInfo</code></td><td>Service status (systemd/docker/process)</td></tr>
<tr><td><code>CommandRequest</code></td><td>Command execution request</td></tr>
<tr><td><code>CommandResult</code></td><td>Command output with exit code</td></tr>
<tr><td><code>Task</code></td><td>Task with status tracking</td></tr>
<tr><td><code>Alert</code></td><td>System alerts</td></tr>
<tr><td><code>Heartbeat</code></td><td>Agent heartbeat with metrics</td></tr>
</table>

<br/>

---

<br/>

## Architecture

```
                    +-------------------------------------+
                    |          Shared Module                |
                    |   models.py / protocol.py / crypto.py |
                    +-------------------------------------+
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
+---------v----------+  +-----------v-----------+  +------------v---------+
|   PC Agent (CLI)   |  |   REST API            |  |  Server Agent        |
|                    |  |   (JSON)              |  |  (FastAPI :8000)     |
|  - Typer CLI       |  |                       |  |                      |
|  - Rich Dashboard  |  |  HTTP/HTTPS           |  |  - Service Monitor   |
|  - Task Manager    |<--+  or Tailscale        +-->|  - Task Executor     |
|  - Multi-Server    |  |                       |  |  - Command Runner    |
+--------------------+  +-----------+-----------+  |  - Alert Generator   |
                                        |           +----------------------+
                                        |
                              +---------v----------+
                              |  Java Client       |
                              |  (11+ / Jackson)   |
                              +--------------------+
```

<br/>

---

<br/>

## Communication Methods

<table>
<tr>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/network.png" alt="net"/> Method</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/settings.png" alt="setup"/> Setup</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/shield.png" alt="security"/> Security</th>
<th><img src="https://img.icons8.com/ios-filled/14/00d4ff/like.png" alt="best"/> Best For</th>
</tr>
<tr>
<td><strong>Tailscale</strong></td>
<td><code>http://&lt;tailscale-ip&gt;:8000</code></td>
<td>WireGuard (always-on)</td>
<td>Remote access</td>
</tr>
<tr>
<td><strong>Cloudflare Tunnel</strong></td>
<td><code>https://agent.mipi.dpdns.org</code></td>
<td>TLS 1.3</td>
<td>Public HTTPS</td>
</tr>
<tr>
<td><strong>SSH Tunnel</strong></td>
<td><code>ssh -L 8000:localhost:8000 pi@host</code></td>
<td>SSH encryption</td>
<td>Quick and secure</td>
</tr>
<tr>
<td><strong>Direct LAN</strong></td>
<td><code>http://192.168.100.10:8000</code></td>
<td>None</td>
<td>Home network</td>
</tr>
</table>

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
|   |   +-- pom.xml
|   |   +-- src/main/java/com/agentbridge/
|   |       +-- Main.java
|   |       +-- client/AgentClient.java
|   |       +-- models/*.java
|   +-- basic_connection.py    Python example
|   +-- service_monitoring.py
|   +-- task_delegation.py
|   +-- multi_server.py
|
+-- deploy/                    [+] Deployment
|   +-- docker-compose.yml
|
+-- docs/                      [+] Documentation
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
|                                              |
+----------------------------------------------+
|  Layer 2: Authentication                     |
|  -----------------------------------------   |
|  API Key (Bearer Token) / mTLS (Mutual TLS) |
|                                              |
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

## Multi-Server

```bash
# Register multiple servers
agent-bridge server add home-pi http://100.109.105.19:8000
agent-bridge server add vps https://agent.myvps.com
agent-bridge server add nas http://192.168.1.100:8000

# Check all at once
agent-bridge status
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
