"""Communication protocol definitions for Agent Bridge."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages exchanged between agents."""

    # Heartbeat
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"

    # Tasks
    TASK_CREATE = "task_create"
    TASK_ASSIGN = "task_assign"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAIL = "task_fail"
    TASK_CANCEL = "task_cancel"

    # Services
    SERVICE_LIST = "service_list"
    SERVICE_STATUS = "service_status"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    SERVICE_RESTART = "service_restart"

    # Commands
    COMMAND_EXECUTE = "command_execute"
    COMMAND_RESULT = "command_result"

    # Server status
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"

    # Logs
    LOG_ENTRY = "log_entry"
    LOG_REQUEST = "log_request"

    # Alerts
    ALERT = "alert"
    ALERT_ACK = "alert_ack"


class AgentMessage(BaseModel):
    """A message envelope for agent-to-agent communication."""

    type: MessageType
    source: str
    destination: str = "*"
    request_id: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = ""


class AgentProtocol:
    """Protocol constants and helpers for Agent Bridge."""

    VERSION = "1.0.0"
    DEFAULT_POLL_INTERVAL = 10  # seconds
    DEFAULT_HEARTBEAT_INTERVAL = 30  # seconds
    MAX_RETRY_ATTEMPTS = 3
    REQUEST_TIMEOUT = 30  # seconds

    @staticmethod
    def encode_message(msg: AgentMessage) -> dict:
        """Encode a message for transmission."""
        return msg.model_dump(mode="json")

    @staticmethod
    def decode_message(data: dict) -> AgentMessage:
        """Decode a received message."""
        return AgentMessage(**data)

    @staticmethod
    def error_response(
        request_id: str, source: str, error: str
    ) -> AgentMessage:
        """Create an error response message."""
        return AgentMessage(
            type=MessageType.COMMAND_RESULT,
            source=source,
            request_id=request_id,
            payload={"error": error, "exit_code": 1},
        )
