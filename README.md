<p align="center">
  <img src="docs/logo.svg" width="180" alt="Agent Bridge Logo"/>
</p>

<h1 align="center">Agent Bridge</h1>

<p align="center">
  <strong>PC → Server communication system for remote monitoring & task execution</strong><br/>
  <em>Your Raspberry Pi at your fingertips — from anywhere in the world.</em>
</p>

<p align="center">
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/python-3.11+-yellow?style=flat-square&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://github.com/erac73/agent-bridge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/></a>
  <a href="https://github.com/erac73/agent-bridge"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build"/></a>
</p>

---

<br/>

## What is this?

```
    ╭──────────────╮                           ╭──────────────╮
    │              │    ── TCP / HTTPS ──►      │              │
    │   PC Agent   │                            │ Server Agent │
    │   (CLI)      │    ◄── JSON / REST ──     │   (FastAPI)  │
    │              │                            │              │
    ╰──────────────╯                           ╰──────────────╯
          │                                           │
          │    ┌─────────────────────────────────┐    │
          │    │   Shared: Models · Protocol · mTLS│   │
          │    └─────────────────────────────────┘    │
          │                                           │
    Monitor services                            Execute commands
    Run remote tasks                            Watch system health
    Live dashboard                              Generate alerts
```

Agent Bridge lets you **monitor**, **control**, and **execute tasks** on your remote servers (Raspberry Pi, VPS, NAS) from your PC — all through a clean REST API and a beautiful CLI.

<br/>

---

<br/>

## Features

<table>
  <tr>
    <td width="50%" valign="top">

### System Monitoring
- CPU, memory, disk, network usage
- Load average & uptime tracking
- Real-time metrics via REST API
- Threshold-based alerts

### Remote Commands
- Execute any shell command remotely
- Timeout control & working directory
- Environment variable support
- Real-time stdout/stderr streaming

    </td>
    <td width="50%" valign="top">

### Service Watchdog
- Monitor **systemd** services
- Monitor **Docker** containers
- Monitor **processes** by name
- Auto-detect service type

### Live Dashboard
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

### Install

```bash
git clone https://github.com/erac73/agent-bridge.git
cd agent-bridge
pip install -r server-agent/requirements.txt
```

### Run Server (on your Pi)

```bash
cd server-agent
python main.py
```

### Run PC Agent (from your computer)

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
<th>Command</th>
<th>Description</th>
<th>Example</th>
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

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │          Shared Module               │
                    │   models.py · protocol.py · crypto.py│
                    └─────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼──────────┐  ┌────────▼────────┐  ┌──────────▼──────────┐
│   PC Agent (CLI)   │  │   REST API      │  │  Server Agent       │
│                    │  │   (JSON)        │  │  (FastAPI :8000)    │
│  · Typer CLI       │  │                 │  │                     │
│  · Rich Dashboard  │  │  HTTP/HTTPS     │  │  · Service Monitor  │
│  · Task Manager    │◄─┤  or Tailscale   ├─►│  · Task Executor    │
│  · Multi-Server    │  │                 │  │  · Command Runner   │
└────────────────────┘  └─────────────────┘  │  · Alert Generator  │
                                             └─────────────────────┘
```

<br/>

---

<br/>

## Communication Methods

| Method | Setup | Security | Best For |
|:-------|:------|:---------|:---------|
| **Tailscale** | `http://<tailscale-ip>:8000` | WireGuard (always-on) | Remote access |
| **Cloudflare Tunnel** | `https://agent.mipi.dpdns.org` | TLS 1.3 | Public HTTPS |
| **SSH Tunnel** | `ssh -L 8000:localhost:8000 pi@host` | SSH encryption | Quick & secure |
| **Direct LAN** | `http://192.168.100.10:8000` | None | Home network |

<br/>

---

<br/>

## Project Structure

```
agent-bridge/
├── shared/                    📦  Shared library
│   ├── models.py              Pydantic data models
│   ├── protocol.py            Message protocol definitions
│   └── crypto.py              mTLS & API key management
│
├── server-agent/              🖥️  Server-side agent
│   ├── main.py                FastAPI entry point
│   ├── agent.py               Core logic
│   ├── api.py                 REST endpoints
│   ├── monitor.py             Service watchdog
│   └── Dockerfile             Container build
│
├── pc-agent/                  💻  PC-side agent
│   ├── main.py                CLI entry point
│   ├── cli.py                 Typer commands
│   ├── task_manager.py        Server registry
│   ├── monitor_dashboard.py   Rich live view
│   └── Dockerfile             Container build
│
├── deploy/                    🐳  Deployment
│   └── docker-compose.yml
│
├── examples/                  📚  Usage examples
│   ├── basic_connection.py
│   ├── service_monitoring.py
│   ├── task_delegation.py
│   └── multi_server.py
│
└── docs/                      📖  Documentation
    ├── architecture.md
    ├── protocol-spec.md
    ├── security.md
    └── deployment.md
```

<br/>

---

<br/>

## Security

Agent Bridge supports **multiple layers** of security:

```
┌────────────────────────────────────────────────────┐
│  Layer 1: Network Encryption                       │
│  ────────────────────────                          │
│  Tailscale (WireGuard) / Cloudflare (TLS 1.3)     │
│                                                    │
├────────────────────────────────────────────────────┤
│  Layer 2: Authentication                           │
│  ─────────────────────────                         │
│  API Key (Bearer Token) / mTLS (Mutual TLS)       │
│                                                    │
├────────────────────────────────────────────────────┤
│  Layer 3: Authorization                            │
│  ──────────────────────                            │
│  Limited user / Sudo rules / Container isolation   │
└────────────────────────────────────────────────────┘
```

<br/>

---

<br/>

## Docker Deployment

```bash
# Build & start the server agent
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
<summary><strong>GET /api/v1/status</strong> — System Status</summary>

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
<summary><strong>POST /api/v1/command</strong> — Execute Command</summary>

```json
// Request
{ "command": "docker", "args": ["ps"], "timeout_seconds": 15 }

// Response
{ "exit_code": 0, "stdout": "...", "duration_seconds": 0.123 }
```

</details>

<details>
<summary><strong>GET /api/v1/services</strong> — Monitored Services</summary>

```json
[
  { "name": "nginx", "type": "systemd", "status": "active", "pid": 1234 },
  { "name": "postgres", "type": "docker", "status": "active", "pid": 5678 }
]
```

</details>

<details>
<summary><strong>GET /api/v1/alerts</strong> — Active Alerts</summary>

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

- **FastAPI** — Async REST API
- **Typer + Rich** — Beautiful CLI
- **Pydantic** — Data validation
- **Docker** — Container support
- **Tailscale** — Secure networking

<br/>

---

<br/>

<p align="center">
  <sub>
    Built by <a href="https://github.com/erac73">erac73</a> · 
    Licensed under <a href="LICENSE">MIT</a>
  </sub>
</p>
