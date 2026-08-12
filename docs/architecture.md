# Architecture

## System Overview

Agent Bridge implements a PC-to-server communication system for remote monitoring and task execution. The architecture follows a client-server model where:

- **PC Agent** (client) runs on your development machine
- **Server Agent** runs on the target server (e.g., Raspberry Pi)

## Communication Flow

```
PC Agent                         Server Agent
    │                                  │
    │  ──── HTTP Request ──────────── │
    │       (REST API + mTLS)         │
    │                                  │
    │  ◀─── JSON Response ────────── │
    │                                  │
    │  ──── POST /api/v1/command ─── │
    │                                  │
    │  ◀─── Command Result ───────── │
```

## Components

### Shared Module (`shared/`)

The shared module contains common data models and protocol definitions used by both agents:

- **`models.py`** — Pydantic data models (Task, ServiceInfo, ServerStatus, Alert, CommandRequest, CommandResponse)
- **`protocol.py`** — Communication protocol types (MessageType enum, AgentMessage envelope)
- **`crypto.py`** — Certificate generation, API key management

### Server Agent (`server-agent/`)

The server agent is a FastAPI application that:

1. **Monitors** system resources (CPU, memory, disk, network)
2. **Watches** services (systemd, Docker containers, processes)
3. **Executes** remote commands with timeout and environment support
4. **Manages** a task queue with status tracking
5. **Generates** alerts for threshold violations

**Components:**
- `main.py` — FastAPI application entry point
- `agent.py` — Core agent logic (identity, heartbeat, task execution)
- `api.py` — REST API endpoints
- `monitor.py` — Service watchdog thread

### PC Agent (`pc-agent/`)

The PC agent provides a CLI interface for:

1. **Server management** — Register, list, and connect to servers
2. **Remote commands** — Execute commands with real-time output
3. **Service monitoring** — View and control remote services
4. **Live dashboard** — Rich-powered real-time monitoring

**Components:**
- `main.py` — Typer CLI entry point
- `cli.py` — CLI commands (server, task, service)
- `task_manager.py` — Server registry and API client
- `monitor_dashboard.py` — Rich live dashboard

## Data Flow

### Command Execution

```
1. PC Agent: CLI → TaskManager.run_command(server, cmd)
2. TaskManager: HTTP POST /api/v1/command → Server Agent
3. Server Agent: agent.execute_command(req) → subprocess.run()
4. Server Agent: Return CommandResponse (exit_code, stdout, stderr)
5. PC Agent: Display result in terminal
```

### Service Monitoring

```
1. Server Agent: monitor._loop() runs every N seconds
2. For each watched service: _get_service_info(name)
3. Detect type (systemd/Docker/process) → Get status
4. Compare with previous status → Generate alerts on changes
5. PC Agent: GET /api/v1/services → Display in table
```

### Heartbeat

```
1. PC Agent: GET /api/v1/agent/heartbeat
2. Server Agent: Collect active/pending tasks, metrics
3. Return Heartbeat (agent_id, active_tasks, metrics)
```

## Security

### API Key Authentication

Simple bearer token authentication:
```
Authorization: Bearer <api-key>
```

### mTLS (Mutual TLS)

Both client and server present certificates:
```
[Server Certificate] ←→ [CA Certificate] ←→ [Client Certificate]
```

### Network Security

| Method | Encryption | Authentication | Best For |
|--------|-----------|---------------|----------|
| Tailscale | WireGuard | Machine identity | Remote access |
| Cloudflare Tunnel | TLS 1.3 | Origin certificates | Public access |
| SSH Tunnel | SSH | SSH keys | Secure local |
| Direct LAN | None | None | Local network |

## Deployment

### Docker (Recommended)

```bash
# Server
docker compose -f deploy/docker-compose.yml up -d

# PC Agent (CLI only)
docker build -t agent-bridge-pc -f pc-agent/Dockerfile .
docker run -it agent-bridge-pc status
```

### Native

```bash
# Server
cd server-agent && python main.py

# PC Agent
cd pc-agent && python main.py status
```

## Scalability

The architecture supports multiple servers:

```
┌─────────────────────────────────────────┐
│                PC Agent                 │
│         (manages all servers)           │
└─────────────────────────────────────────┘
    │              │              │
    ↓              ↓              ↓
┌────────┐  ┌────────┐  ┌────────┐
│ Pi     │  │ VPS    │  │ NAS    │
│ :8000  │  │ :8000  │  │ :8000  │
└────────┘  └────────┘  └────────┘
```

Each server runs its own agent, and the PC agent communicates with all of them independently.
