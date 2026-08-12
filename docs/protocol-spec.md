# Protocol Specification

## Overview

Agent Bridge uses a simple HTTP/JSON protocol for communication between the PC agent and server agent.

## Base URL

```
http://<host>:8000
```

## Authentication

### API Key (Bearer Token)

```http
Authorization: Bearer <api-key>
```

### mTLS

When TLS is enabled, both client and server present X.509 certificates.

## Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe |

### Agent Info

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/agent` | Agent identity |
| GET | `/api/v1/agent/heartbeat` | Heartbeat with metrics |

### Server Status

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/status` | Full system status |

**Response:**
```json
{
  "hostname": "raspberrypi",
  "cpu_percent": 12.5,
  "cpu_count": 4,
  "load_avg_1": 0.5,
  "load_avg_5": 0.3,
  "load_avg_15": 0.2,
  "memory_total_gb": 7.64,
  "memory_used_gb": 2.1,
  "memory_percent": 27.5,
  "disk_total_gb": 27.0,
  "disk_used_gb": 23.8,
  "disk_percent": 88.1,
  "net_sent_gb": 1.2,
  "net_recv_gb": 5.8,
  "uptime_seconds": 123456,
  "kernel_version": "6.12.96",
  "services": [...]
}
```

### Services

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/services` | List watched services |
| GET | `/api/v1/services/{name}` | Get specific service |
| POST | `/api/v1/services/{name}/watch` | Add to watch list |
| POST | `/api/v1/services/{name}/restart` | Restart service |
| POST | `/api/v1/services/{name}/stop` | Stop service |
| POST | `/api/v1/services/{name}/start` | Start service |

**Service Object:**
```json
{
  "name": "nginx",
  "type": "systemd",
  "status": "active",
  "health": null,
  "pid": 1234,
  "memory_mb": 15.2,
  "cpu_percent": 0.0,
  "metadata": {}
}
```

**Status values:** `active`, `inactive`, `failed`, `activating`, `deactivating`, `unknown`

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/tasks` | List tasks |
| GET | `/api/v1/tasks/{id}` | Get task |
| POST | `/api/v1/tasks` | Create task |
| POST | `/api/v1/tasks/{id}/run` | Execute task |

**Task Object:**
```json
{
  "id": "task-123",
  "title": "Check disk usage",
  "command": "df -h",
  "args": [],
  "env": {},
  "working_dir": null,
  "timeout_seconds": 30,
  "status": "completed",
  "assigned_to": "server-raspberrypi",
  "created_at": "2026-08-11T12:00:00Z",
  "started_at": "2026-08-11T12:00:01Z",
  "completed_at": "2026-08-11T12:00:02Z",
  "exit_code": 0,
  "result": "...",
  "error": null,
  "priority": "high"
}
```

**Task statuses:** `pending`, `assigned`, `running`, `completed`, `failed`, `cancelled`, `timeout`

### Commands

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/command` | Execute a command |

**Request:**
```json
{
  "request_id": "req-abc",
  "command": "docker",
  "args": ["ps", "--format", "table {{.Names}}\t{{.Status}}"],
  "timeout_seconds": 15,
  "working_dir": "/home/serpico",
  "env": {"DOCKER_HOST": "unix:///var/run/docker.sock"}
}
```

**Response:**
```json
{
  "request_id": "req-abc",
  "exit_code": 0,
  "stdout": "NAME      STATUS\n...",
  "stderr": "",
  "started_at": "2026-08-11T12:00:00Z",
  "completed_at": "2026-08-11T12:00:01Z",
  "duration_seconds": 0.123
}
```

### Alerts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/alerts` | List active alerts |
| POST | `/api/v1/alerts/{id}/ack` | Acknowledge alert |

**Alert Object:**
```json
{
  "id": "alert-abc",
  "severity": "warning",
  "title": "Disk usage high",
  "message": "Disk at 92% (24.9GB / 27.0GB)",
  "source": "resource_monitor",
  "timestamp": "2026-08-11T12:00:00Z",
  "acknowledged": false,
  "resolved": false
}
```

**Severity levels:** `info`, `warning`, `error`, `critical`

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad request / validation error |
| 401 | Authentication required |
| 403 | Forbidden |
| 404 | Resource not found |
| 500 | Internal server error |

**Error Response:**
```json
{
  "detail": "Service 'foo' not found"
}
```

## Message Envelope (Internal)

The shared protocol defines a generic message envelope:

```python
class AgentMessage:
    id: str              # Unique message ID
    type: MessageType    # heartbeat | command | response | alert | task | status | register | unregister
    sender_id: str       # Agent sending the message
    recipient_id: str    # Target agent
    timestamp: datetime  # UTC timestamp
    payload: dict        # Message-specific data
    signature: str       # HMAC signature (optional)
```

## Rate Limiting

- Max concurrent commands: 5
- Command timeout: 60 seconds (default)
- Heartbeat interval: 30 seconds
- Service check interval: 15 seconds
