FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    langchain==0.3.25 \
    langchain-anthropic==0.3.15 \
    langgraph==0.4.8 \
    flake8==7.3.0 \
    detect-secrets==1.5.0 \
    pip-audit==2.9.0 \
    pytest==8.3.5

WORKDIR /workspace
