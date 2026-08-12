"""Server Agent — Monitors services and executes tasks from the PC agent."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from agent import ServerAgent
from api import create_router
from monitor import ServiceMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("server-agent")

agent = ServerAgent()
monitor = ServiceMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server Agent starting...")
    await agent.start()
    monitor.start()
    yield
    logger.info("Server Agent shutting down...")
    monitor.stop()
    await agent.stop()


app = FastAPI(
    title="Agent Bridge — Server Agent",
    description="Monitors server services and executes remote tasks.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(create_router(agent, monitor))


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {
        "status": "healthy" if agent.is_ready else "starting",
        "agent_id": agent.agent_id,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
