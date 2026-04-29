# Prometheus MCP Server Dockerfile
# 多阶段构建：减小镜像体积

# 阶段1：构建依赖
FROM python:3.14-slim AS builder

WORKDIR /app

# 安装依赖到独立目录
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir -e .

# 阶段2：运行时镜像（使用 alpine 减小体积）
FROM python:3.14-alpine

WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 只复制源代码
COPY src/ ./src/
COPY pyproject.toml README.md ./

# 默认命令 - 使用 stdio 传输（MCP 标准）
CMD ["python", "-m", "prometheus_mcp"]
