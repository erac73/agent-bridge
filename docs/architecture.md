# Architecture

## System Overview

Agent Bridge implements a **client-server architecture** for PC-to-server communication. The design follows a layered approach where each component has a clear responsibility.

```
+==================================================================+
|                        USER INTERFACE                             |
+==================================================================+
|  PC Agent CLI (Typer + Rich)  |  Java Client (HttpClient)        |
+------------------------------------------------------------------+
|                        TRANSPORT LAYER                            |
+------------------------------------------------------------------+
|  httpx (Python) / HttpClient (Java)  ->  HTTP/HTTPS              |
+------------------------------------------------------------------+
|                     NETWORK LAYER                                 |
+------------------------------------------------------------------+
|  Tailscale (WireGuard) | Cloudflare (TLS) | SSH | LAN            |
+------------------------------------------------------------------+
|                     SERVER LAYER                                  |
+------------------------------------------------------------------+
|  FastAPI + Uvicorn (REST API)                                    |
+------------------------------------------------------------------+
|                     PROCESSING LAYER                              |
+------------------------------------------------------------------+
|  psutil (system) | Docker SDK | subprocess (commands)            |
+------------------------------------------------------------------+
|                     DATA LAYER                                    |
+------------------------------------------------------------------+
|  Pydantic (Python) | Jackson (Java) | JSON serialization         |
+------------------------------------------------------------------+
```

## Component Diagram

```
                              +------------------+
                              |   User (Human)   |
                              +--------+---------+
                                       |
                              +--------v---------+
                              |                  |
                              |    PC Agent      |
                              |    (Client)      |
                              |                  |
                              |  +------------+  |
                              |  | CLI (Typer)|  |
                              |  +-----+------+  |
                              |        |         |
                              |  +-----v------+  |
                              |  |Task Manager|  |
                              |  +-----+------+  |
                              |        |         |
                              |  +-----v------+  |
                              |  | HTTP Client|  |
                              |  |  (httpx)   |  |
                              |  +-----+------+  |
                              +--------+---------+
                                       |
                              ~~~~ network ~~~~
                                       |
                              +--------v---------+
                              |                  |
                              |  Server Agent    |
                              |  (FastAPI)       |
                              |                  |
                              |  +------------+  |
                              |  | REST API   |  |
                              |  | (FastAPI)  |  |
                              |  +-----+------+  |
                              |        |         |
                              |  +-----v------+  |
                              |  | Agent Core |  |
                              |  +-----+------+  |
                              |        |         |
                              |  +-----v------+  |
                              |  |  Monitor   |  |
                              |  | (watchdog) |  |
                              |  +-----+------+  |
                              |        |         |
                              +--------+---------+
                                       |
                    +------------------+------------------+
                    |                  |                  |
            +-------v-------+  +-------v-------+  +-------v-------+
            |    psutil     |  |  Docker SDK   |  |  subprocess   |
            |  (system)     |  | (containers)  |  |  (commands)   |
            +---------------+  +---------------+  +---------------+
```

## Data Flow

### Command Execution Flow

```
User                PC Agent              Network           Server Agent           OS
 |                    |                     |                    |                   |
 |  "docker ps"       |                     |                    |                   |
 +------------------> |                     |                    |                   |
 |                    |  HTTP POST           |                    |                   |
 |                    | /api/v1/command      |                    |                   |
 |                    | {"command":"docker"} |                    |                   |
 |                    +--------------------> |                    |                   |
 |                    |                     |  HTTP Request       |                   |
 |                    |                     +------------------> |                   |
 |                    |                     |                    |  subprocess.run()  |
 |                    |                     |                    +------------------> |
 |                    |                     |                    |                    | docker ps
 |                    |                     |                    |                    |
 |                    |                     |                    |  stdout="..."      |
 |                    |                     |                    | <-----------------+
 |                    |                     |  JSON Response      |                   |
 |                    |                     | <-----------------+                   |
 |                    |  {"exit_code":0,...} |                    |                   |
 |                    | <--------------------+                    |                   |
 |  "Exit Code: 0"    |                     |                    |                   |
 | <------------------+                     |                    |                   |
```

### Service Monitoring Flow

```
Server Agent                    Monitor Thread               OS
     |                               |                        |
     |  start()                      |                        |
     +--------------------------->   |                        |
     |                               |  every 15 seconds      |
     |                               +----------------------> |
     |                               |                        |
     |                               |  systemctl is-active   |
     |                               +----------------------> |
     |                               |                        |
     |                               |  active                |
     |                               | <----------------------+
     |                               |                        |
     |                               |  docker ps             |
     |                               +----------------------> |
     |                               |                        |
     |                               |  container status      |
     |                               | <----------------------+
     |                               |                        |
     |  status changed!              |                        |
     | <------------------------------+                        |
     |                               |                        |
     |  generate alert               |                        |
     +--------------------------->   |                        |
     |                               |                        |
```

## Shared Module

The shared module defines the data models used by both PC and Server agents:

```
+-----------------------------------------------+
|              shared/                           |
+-----------------------------------------------+
|                                                |
|  models.py          Defines all data types:    |
|  +-------+         - Task                      |
|  | Task  |         - ServiceInfo               |
|  +-------+         - ServerStatus              |
|  | id    |         - CommandRequest            |
|  | title |         - CommandResponse           |
|  | cmd   |         - Alert                     |
|  | status|         - Heartbeat                 |
|  +-------+         - AgentInfo                 |
|                     - HealthStatus              |
|                                                |
|  protocol.py       Defines message types:      |
|                     - MessageType enum          |
|                     - AgentMessage envelope     |
|                                                |
|  crypto.py         Security utilities:         |
|                     - Certificate generation   |
|                     - API key hashing          |
|                                                |
+-----------------------------------------------+
```

## Server Agent Internals

```
+--------------------------------------------------+
|                  Server Agent                     |
+--------------------------------------------------+
|                                                   |
|  main.py                                         |
|  +--------------------------------------------+  |
|  | FastAPI app with lifespan                  |  |
|  | - Creates ServerAgent instance             |  |
|  | - Starts ServiceMonitor thread             |  |
|  | - Includes API router                      |  |
|  +--------------------------------------------+  |
|                                                   |
|  agent.py                                        |
|  +--------------------------------------------+  |
|  | ServerAgent class                          |  |
|  | - get_info()         -> AgentInfo          |  |
|  | - get_heartbeat()    -> Heartbeat          |  |
|  | - execute_command()  -> CommandResponse    |  |
|  | - assign_task()      -> Task               |  |
|  | - run_task()         -> Task               |  |
|  +--------------------------------------------+  |
|                                                   |
|  api.py                                          |
|  +--------------------------------------------+  |
|  | REST Endpoints                             |  |
|  | GET  /api/v1/agent       -> AgentInfo      |  |
|  | GET  /api/v1/status      -> ServerStatus   |  |
|  | GET  /api/v1/services    -> [ServiceInfo]  |  |
|  | POST /api/v1/command     -> CommandResponse|  |
|  | GET  /api/v1/tasks       -> [Task]         |  |
|  | GET  /api/v1/alerts      -> [Alert]        |  |
|  +--------------------------------------------+  |
|                                                   |
|  monitor.py                                      |
|  +--------------------------------------------+  |
|  | ServiceMonitor class (background thread)   |  |
|  | - _check_services()                        |  |
|  | - _get_service_info()                      |  |
|  |   -> _check_systemd()                      |  |
|  |   -> _check_docker()                       |  |
|  |   -> _check_process()                      |  |
|  | - _check_resources()                       |  |
|  +--------------------------------------------+  |
|                                                   |
+--------------------------------------------------+
```

## PC Agent Internals

```
+--------------------------------------------------+
|                  PC Agent                         |
+--------------------------------------------------+
|                                                   |
|  main.py                                         |
|  +--------------------------------------------+  |
|  | Typer app with sub-commands                |  |
|  | - server (add, list, status, remove)       |  |
|  | - task (run, list)                         |  |
|  | - service (list, restart, watch)           |  |
|  | - status, dashboard, config                |  |
|  +--------------------------------------------+  |
|                                                   |
|  cli.py                                          |
|  +--------------------------------------------+  |
|  | CLI Commands                               |  |
|  | - server_add()                             |  |
|  | - server_list()                            |  |
|  | - server_status()                          |  |
|  | - task_run()                               |  |
|  | - service_list()                           |  |
|  | - service_restart()                        |  |
|  | - dashboard()                              |  |
|  +--------------------------------------------+  |
|                                                   |
|  task_manager.py                                 |
|  +--------------------------------------------+  |
|  | TaskManager class                          |  |
|  | - add_server()                             |  |
|  | - remove_server()                          |  |
|  | - list_servers()                           |  |
|  | - api_get()  -> JSON                       |  |
|  | - api_post() -> JSON                       |  |
|  | - run_command() -> dict                    |  |
|  +--------------------------------------------+  |
|                                                   |
|  monitor_dashboard.py                            |
|  +--------------------------------------------+  |
|  | Rich Live Dashboard                        |  |
|  | - make_header()                            |  |
|  | - make_system_panel()                      |  |
|  | - make_services_panel()                    |  |
|  | - make_alerts_panel()                      |  |
|  | - run_dashboard()                          |  |
|  +--------------------------------------------+  |
|                                                   |
+--------------------------------------------------+
```

## Java Client Architecture

```
+--------------------------------------------------+
|              Java Client                          |
+--------------------------------------------------+
|                                                   |
|  AgentClient.java                                |
|  +--------------------------------------------+  |
|  | HttpClient (Java 11+)                     |  |
|  | - healthCheck()       -> HealthStatus      |  |
|  | - getAgentInfo()      -> AgentInfo         |  |
|  | - getServerStatus()   -> ServerStatus      |  |
|  | - getServices()       -> List<ServiceInfo> |  |
|  | - executeCommand()    -> CommandResult     |  |
|  | - getTasks()          -> List<Task>        |  |
|  | - createTask()        -> Task              |  |
|  | - runTask()           -> Task              |  |
|  | - getAlerts()         -> List<Alert>       |  |
|  +--------------------------------------------+  |
|                                                   |
|  models/                                         |
|  +--------------------------------------------+  |
|  | Jackson-annotated POJOs                    |  |
|  | AgentInfo, ServerStatus, ServiceInfo       |  |
|  | CommandRequest, CommandResult              |  |
|  | Task, Alert, Heartbeat, HealthStatus       |  |
|  +--------------------------------------------+  |
|                                                   |
+--------------------------------------------------+
```

## Security Architecture

```
+--------------------------------------------------+
|              Security Layers                      |
+--------------------------------------------------+
|                                                   |
|  Layer 1: Network Encryption                     |
|  +--------------------------------------------+  |
|  | Tailscale: WireGuard UDP tunnel            |  |
|  | Cloudflare: TLS 1.3 + WAF                  |  |
|  | SSH: Encrypted port forwarding             |  |
|  | LAN: No encryption (trusted only)          |  |
|  +--------------------------------------------+  |
|                                                   |
|  Layer 2: Authentication                         |
|  +--------------------------------------------+  |
|  | API Key: Bearer token in header            |  |
|  | mTLS: Mutual certificate verification      |  |
|  +--------------------------------------------+  |
|                                                   |
|  Layer 3: Authorization                          |
|  +--------------------------------------------+  |
|  | Run as limited user (not root)             |  |
|  | Sudo rules for specific commands           |  |
|  | Docker container isolation                 |  |
|  +--------------------------------------------+  |
|                                                   |
+--------------------------------------------------+
```

## Deployment Architecture

```
+--------------------------------------------------+
|              Deployment Options                   |
+--------------------------------------------------+
|                                                   |
|  Option 1: Native                                |
|  +--------------------------------------------+  |
|  | Server: python main.py (systemd service)   |  |
|  | PC: python main.py (direct execution)      |  |
|  +--------------------------------------------+  |
|                                                   |
|  Option 2: Docker                                |
|  +--------------------------------------------+  |
|  | Server: docker compose up -d               |  |
|  | PC: docker build + run                     |  |
|  +--------------------------------------------+  |
|                                                   |
|  Option 3: Mixed                                 |
|  +--------------------------------------------+  |
|  | Server: Docker (port 8000)                 |  |
|  | PC: Native Python/Java                     |  |
|  +--------------------------------------------+  |
|                                                   |
+--------------------------------------------------+
```

## Scalability

The architecture supports multiple servers:

```
                    +------------------+
                    |    PC Agent      |
                    |  (manages all)   |
                    +--------+---------+
                             |
            +----------------+----------------+
            |                |                |
    +-------v-------+ +-----v-------+ +------v------+
    |   Pi 5        | |   VPS       | |   NAS       |
    |   :8000       | |   :8000     | |   :8000     |
    |               | |             | |             |
    | Server Agent  | | Server Agent| | Server Agent|
    +---------------+ +-------------+ +-------------+
```

Each server runs its own agent, and the PC agent communicates with all of them independently. There is no central coordinator — each connection is direct.

## Technology Matrix

| Component | Technology | Why This Choice |
|-----------|-----------|----------------|
| REST API | FastAPI | Async, auto-docs, Pydantic validation |
| HTTP Server | Uvicorn | High performance ASGI server |
| HTTP Client (Python) | httpx | Async, modern, well-maintained |
| HTTP Client (Java) | HttpClient | Built-in, no dependencies |
| JSON (Python) | Pydantic | Type validation, serialization |
| JSON (Java) | Jackson | Industry standard, mature |
| System Metrics | psutil | Cross-platform, comprehensive |
| Docker Integration | docker SDK | Direct socket communication |
| CLI Framework | Typer | Modern, type-safe, auto-help |
| Terminal UI | Rich | Beautiful tables, live views |
| VPN | Tailscale | WireGuard, zero-config |
| Containerization | Docker | Reproducible, isolated |
