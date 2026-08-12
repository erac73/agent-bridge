# Deployment

## Quick Start (Raspberry Pi)

### 1. Clone and Install

```bash
cd /home/serpico
git clone https://github.com/erac73/agent-bridge.git
cd agent-bridge

# Server agent
pip install -r server-agent/requirements.txt
```

### 2. Configure

Edit `server-agent/config.yaml`:
```yaml
api_key: "your-secret-key"
watched_services:
  - ssh
  - docker
  - nginx
monitor_interval: 15
```

### 3. Run

```bash
cd server-agent
python main.py
```

### 4. Verify

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/api/v1/status
```

## Docker Deployment

### Server Agent

```bash
cd /home/serpico/agent-bridge

# Build and start
docker compose -f deploy/docker-compose.yml up -d

# Check logs
docker logs -f server-agent

# Stop
docker compose -f deploy/docker-compose.yml down
```

### Docker Compose Configuration

Edit `deploy/docker-compose.yml` to mount your config:
```yaml
volumes:
  - ./config.yaml:/app/server-agent/config.yaml:ro
  - /var/run/docker.sock:/var/run/docker.sock:ro
  - /etc/systemd:/etc/systemd:ro
```

## Systemd Service

Create `/etc/systemd/system/server-agent.service`:

```ini
[Unit]
Description=Agent Bridge Server
After=network.target docker.service

[Service]
Type=simple
User=serpico
WorkingDirectory=/home/serpico/agent-bridge/server-agent
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable server-agent
sudo systemctl start server-agent
```

## PC Agent Setup

### Install

```bash
cd /path/to/agent-bridge/pc-agent
pip install -r requirements.txt
```

### Register Server

```bash
# Via Tailscale (recommended)
python main.py server add mypi http://100.109.105.19:8000 --api-key <key>

# Via Cloudflare Tunnel
python main.py server add mypi https://mipi.dpdns.org --api-key <key>

# Via SSH Tunnel
ssh -L 8000:localhost:8000 serpico@192.168.100.10
python main.py server add mypi http://localhost:8000 --api-key <key>
```

### Verify

```bash
python main.py server list
python main.py server status mypi
```

## Remote Access Options

### Option 1: Tailscale (Recommended)

```bash
# On Pi
sudo tailscale up

# On PC
# Tailscale IP: 100.109.105.19
python main.py server add mypi http://100.109.105.19:8000
```

### Option 2: Cloudflare Tunnel

Add to `/etc/cloudflared/config.yml`:
```yaml
ingress:
  - hostname: agent.mipi.dpdns.org
    service: http://localhost:8000
  - service: http_status:404
```

```bash
sudo cloudflared tunnel route dns 17364353-0493-4c12-ba18-8260cb8c4f8d agent.mipi.dpdns.org
sudo systemctl restart cloudflared
```

### Option 3: SSH Tunnel

```bash
# Forward port 8000
ssh -L 8000:localhost:8000 serpico@192.168.100.10

# Connect to localhost
python main.py server add mypi http://localhost:8000
```

### Option 4: Direct LAN

```bash
python main.py server add mypi http://192.168.100.10:8000
```

## Multi-Server Setup

```bash
# Register multiple servers
python main.py server add home-pi http://100.109.105.19:8000
python main.py server add vps https://agent.myvps.com --api-key <key>
python main.py server add nas http://192.168.1.100:8000

# Check all
python main.py status
```

## Monitoring

### Watch Services

```bash
python main.py service watch mypi ssh
python main.py service watch mypi docker
python main.py service watch mypi nginx
```

### Live Dashboard

```bash
python main.py dashboard mypi
```

## Troubleshooting

### Agent not starting

```bash
# Check logs
docker logs server-agent
journalctl -u server-agent

# Check port
lsof -i :8000

# Test connection
curl -v http://localhost:8000/health/live
```

### Connection refused

1. Check agent is running: `curl localhost:8000/health/live`
2. Check firewall: `sudo ufw status`
3. Check Tailscale: `tailscale status`
4. Check Docker: `docker ps | grep server-agent`

### Command timeout

Increase timeout in task creation or config:
```python
task_mgr.run_command("mypi", "long-command", timeout=120)
```
