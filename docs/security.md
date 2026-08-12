# Security

## Authentication

### API Keys

Agent Bridge supports API key authentication via Bearer tokens.

**Generate a key:**
```bash
python -c "from shared.crypto import generate_api_key; print(generate_api_key())"
```

**Configure on server:** Set `api_key` in `server-agent/config.yaml` or environment variable `AGENT_API_KEY`.

**Configure on PC:** Pass `--api-key` when adding a server:
```bash
agent-bridge server add mypi http://100.109.105.19:8000 --api-key <your-key>
```

### mTLS (Mutual TLS)

For stronger authentication, use mutual TLS where both client and server present certificates.

**Generate certificates:**
```bash
python -c "from shared.crypto import generate_certificates; generate_certificates('/path/to/certs')"
```

This creates:
- `ca.crt` — Certificate Authority
- `ca.key` — CA private key
- `agent.crt` — Agent certificate
- `agent.key` — Agent private key

**Enable on server:** Set `tls.enabled: true` in `config.yaml` and provide cert paths.

**Verify on client:** Pass `--ca-cert` and `--client-cert` flags or set in config.

## Encryption in Transit

| Method | Encryption | Recommendation |
|--------|-----------|---------------|
| Tailscale | WireGuard (always-on) | Best for remote access |
| Cloudflare Tunnel | TLS 1.3 | Best for public access |
| SSH Tunnel | SSH encryption | Good for temporary access |
| Direct LAN | None | Only for trusted networks |

## Network Security

### Firewall Rules

```bash
# Allow only Tailscale interface
sudo ufw allow in on tailscale0 to any port 8000

# Or allow only from specific IP
sudo ufw allow from 100.109.105.19 to any port 8000
```

### Binding

The server agent binds to `0.0.0.0:8000` by default. For security, consider:

1. **Local binding only:** Change to `127.0.0.1:8000` and use SSH tunnel
2. **Firewall rules:** Restrict access to specific IPs
3. **Reverse proxy:** Use nginx/caddy with TLS termination

## Command Execution Security

### Restrictions

Commands are executed with the server agent's user permissions. To restrict:

1. **Run as limited user:** Don't run the agent as root
2. **Command whitelist:** Filter allowed commands in `agent.py`
3. **Sudo rules:** Configure specific sudo permissions for the agent user
4. **Container isolation:** Run in Docker with limited capabilities

### Recommended: Limited User

```bash
# Create dedicated user
sudo useradd -r -s /bin/false agent-bridge

# Grant specific sudo permissions
echo "agent-bridge ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx, /usr/bin/docker restart *" | sudo tee /etc/sudoers.d/agent-bridge
```

## Secrets Management

### Environment Variables

```bash
# Server
export AGENT_API_KEY="your-secret-key"

# Don't commit secrets to git
```

### Config Files

- Keep `config.yaml` out of version control
- Use `.gitignore` to exclude sensitive files
- Use Docker secrets for container deployments

## Docker Security

### Container Capabilities

Minimize Docker container capabilities:

```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Only if needed
```

### Read-Only Filesystem

```yaml
read_only: true
tmpfs:
  - /tmp
```

### No Root

```yaml
user: "1000:1000"
```

## Monitoring

### Alert on Security Events

Monitor for:
- Failed authentication attempts
- Unusual command patterns
- High resource usage (potential crypto mining)
- Unexpected service restarts

### Logs

Agent Bridge logs all commands and API access. Review logs regularly:

```bash
# Docker logs
docker logs server-agent --tail 100

# Systemd journal
journalctl -u server-agent -f
```

## Best Practices

1. **Always use authentication** — API key at minimum, mTLS preferred
2. **Encrypt traffic** — Tailscale or Cloudflare Tunnel for remote access
3. **Limit commands** — Don't allow arbitrary root commands
4. **Monitor access** — Review logs and alerts regularly
5. **Update regularly** — Keep dependencies and system packages updated
6. **Principle of least privilege** — Run agents with minimal permissions
7. **Network segmentation** — Isolate server agent from public internet
8. **Backup certificates** — Store cert keys securely (not in git)
