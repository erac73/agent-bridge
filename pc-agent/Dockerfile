FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
COPY pc-agent/ /app/pc-agent/

RUN pip install --no-cache-dir -r /app/pc-agent/requirements.txt

WORKDIR /app/pc-agent

ENTRYPOINT ["python", "main.py"]
