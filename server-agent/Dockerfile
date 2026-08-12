FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl sudo systemctl \
    && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
COPY server-agent/ /app/server-agent/

RUN pip install --no-cache-dir -r /app/server-agent/requirements.txt

WORKDIR /app/server-agent

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')" || exit 1

CMD ["python", "main.py"]
