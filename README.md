# Agent Bridge

PC-to-server agent communication system for remote monitoring and task execution.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       PC Agent (Client)                        │
│  CLI: agent-bridge status | task run | service list | dashboard │
├─────────────────────────────────────────────────────────────────┤
│              Task Manager ←→ API Client (httpx)                 │
│                   ↓ REST + mTLS                                 │
├─────────────────────────────────────────────────────────────────┤
│              shared/ — Pydantic Models + Protocol               │
├─────────────────────────────────────────────────────────────────┤
│              TCP (Tailscale) or HTTPS (Cloudflare Tunnel)       │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    Server Agent (FastAPI)                       │
│              Port 8000 — Auto-discovery + mTLS                  │
├─────────────────────────────────────────────────────────────────┤
│  api.py (REST) │ monitor.py (watchdog) │ task_executor (run)   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Server Side (Raspberry Pi)

```bash
cd /home/serpico/agent-bridge
pip install -r server-agent/requirements.txt

# Run the server agent
cd server-agent
python main.py

# Or run via Docker
docker compose -f ../deploy/docker-compose.yml up server-agent -d
```

The server agent runs on port 8000 and exposes:
- `GET /api/v1/agent` — Agent info
- `GET /api/v1/status` — System metrics
- `GET /api/v1/services` — Watched services
- `POST /api/v1/command` — Execute remote commands
- `GET /api/v1/tasks` — List tasks
- `GET /api/v1/alerts` — Active alerts

### PC Side (Windows/Mac/Linux)

```bash
cd pc-agent
pip install -r requirements.txt

# Add your server
python main.py server add mypi http://100.109.105.19:8000

# Check status
python main.py server status mypi

# Run a command
python main.py task run mypi "docker ps"

# Live dashboard
python main.py dashboard mypi

# Monitor services
python main.py service list mypi
```

## Configuration

PC Agent config: `~/.config/agent-bridge/config.yaml`

```yaml
servers:
  mypi:
    name: mypi
    url: http://100.109.105.19:8000
    api_key: ""
```

## Project Structure

```
agent-bridge/
├── shared/                   # Shared library (Pydantic models, protocol, crypto)
│   ├── models.py            # Task, ServiceInfo, ServerStatus, Alert, etc.
│   ├── protocol.py          # Message types, protocol definitions
│   └── crypto.py            # mTLS cert generation, API key management
├── server-agent/             # Server-side agent (FastAPI)
│   ├── main.py              # FastAPI app entry point
│   ├── agent.py             # Core agent logic
│   ├── api.py               # REST endpoints
│   ├── monitor.py           # Service watchdog (systemd + Docker + process)
│   ├── config.yaml          # Server configuration
│   ├── requirements.txt
│   └── Dockerfile
├── pc-agent/                 # PC-side agent (CLI)
│   ├── main.py              # Typer CLI entry point
│   ├── cli.py               # CLI commands
│   ├── task_manager.py      # Server registry + API client
│   ├── monitor_dashboard.py # Rich live dashboard
│   ├── requirements.txt
│   └── Dockerfile
├── deploy/                   # Deployment configuration
│   └── docker-compose.yml
├── examples/                 # Usage examples
│   ├── basic_connection.py
│   ├── service_monitoring.py
│   ├── task_delegation.py
│   └── multi_server.py
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── protocol-spec.md
│   ├── security.md
│   └── deployment.md
└── README.md
```

## Features

- **System Monitoring** — CPU, memory, disk, network, load average
- **Service Watchdog** — Monitor systemd services, Docker containers, and processes
- **Remote Command Execution** — Execute shell commands with timeout and working directory
- **Task Queue** — Delegate tasks with status tracking
- **Alerts** — Threshold-based alerts for system resources
- **Live Dashboard** — Rich-powered real-time monitoring
- **mTLS Support** — Mutual TLS for secure communication
- **Multi-Server** — Manage multiple servers from one PC

## Communication Methods

| Method | Use Case | Setup |
|--------|----------|-------|
| **Tailscale** | Remote access (recommended) | `http://<tailscale-ip>:8000` |
| **Cloudflare Tunnel** | Public HTTPS | Configure route in Cloudflare |
| **SSH Tunnel** | Secure local access | `ssh -L 8000:localhost:8000 pi@host` |
| **Direct LAN** | Home network | `http://<local-ip>:8000` |

## License

MIT
