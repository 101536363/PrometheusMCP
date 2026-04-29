# Prometheus MCP Server Dockerfile

FROM python:3.14-slim

WORKDIR /app

COPY src/ ./src/
COPY pyproject.toml README.md ./

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "prometheus_mcp"]
