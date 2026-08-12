"""Cryptographic utilities for Agent Bridge authentication."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import ssl
import subprocess
from pathlib import Path


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_hex(32)


def hash_api_key(key: str) -> str:
    """Hash an API key with SHA-256 for storage."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, hashed: str) -> bool:
    """Verify an API key against its hash."""
    return hmac.compare_digest(hash_api_key(key), hashed)


def generate_ca_cert(
    ca_dir: str = "/etc/agent-bridge/certs",
    ca_name: str = "AgentBridge CA",
) -> tuple[Path, Path]:
    """Generate a self-signed CA certificate and key.

    Returns (cert_path, key_path).
    """
    ca_path = Path(ca_dir)
    ca_path.mkdir(parents=True, exist_ok=True)

    cert_path = ca_path / "ca.crt"
    key_path = ca_path / "ca.key"

    if cert_path.exists() and key_path.exists():
        return cert_path, key_path

    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-days", "365",
            "-nodes",
            "-subj", f"/CN={ca_name}",
        ],
        check=True,
        capture_output=True,
    )
    return cert_path, key_path


def generate_agent_cert(
    agent_id: str,
    ca_dir: str = "/etc/agent-bridge/certs",
) -> tuple[Path, Path]:
    """Generate a client certificate signed by the CA.

    Returns (cert_path, key_path).
    """
    ca_path = Path(ca_dir)
    cert_dir = ca_path / "agents"
    cert_dir.mkdir(parents=True, exist_ok=True)

    agent_cert_dir = cert_dir / agent_id
    agent_cert_dir.mkdir(exist_ok=True)

    cert_path = agent_cert_dir / "agent.crt"
    key_path = agent_cert_dir / "agent.key"
    csr_path = agent_cert_dir / "agent.csr"

    ca_cert = ca_path / "ca.crt"
    ca_key = ca_path / "ca.key"

    if cert_path.exists() and key_path.exists():
        return cert_path, key_path

    # Generate key and CSR
    subprocess.run(
        [
            "openssl", "req", "-newkey", "rsa:2048",
            "-keyout", str(key_path),
            "-out", str(csr_path),
            "-nodes",
            "-subj", f"/CN={agent_id}",
        ],
        check=True,
        capture_output=True,
    )

    # Sign with CA
    subprocess.run(
        [
            "openssl", "x509", "-req",
            "-in", str(csr_path),
            "-CA", str(ca_cert),
            "-CAkey", str(ca_key),
            "-CAcreateserial",
            "-out", str(cert_path),
            "-days", "30",
        ],
        check=True,
        capture_output=True,
    )

    csr_path.unlink(missing_ok=True)
    return cert_path, key_path


def create_tls_context(
    cert_path: str | Path,
    key_path: str | Path,
    ca_path: str | Path,
    verify_peer: bool = True,
) -> ssl.SSLContext:
    """Create an mTLS SSL context for server or client use."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3

    ctx.load_cert_chain(cert_path, key_path)
    if verify_peer:
        ctx.load_verify_locations(ca_path)
        ctx.verify_mode = ssl.CERT_REQUIRED
    else:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    return ctx
