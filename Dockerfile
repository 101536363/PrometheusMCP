# Prometheus MCP Server Dockerfile

FROM python:3.14-slim

WORKDIR /app

# 复制所有源代码和配置
COPY src/ ./src/
COPY pyproject.toml README.md ./

# 安装依赖
RUN pip install --no-cache-dir -e .

# 默认命令 - 使用 stdio 传输（MCP 标准）
CMD ["python", "-m", "prometheus_mcp"]
