# Prometheus MCP 规格文档

## 项目概述

- **项目名称**: prometheus-mcp
- **类型**: MCP Server (Model Context Protocol)
- **功能**: Prometheus/Alertmanager API 封装，直接 URL 查询，无需配置实例
- **技术栈**: Python 3.10+, FastMCP, httpx, Pydantic

## 架构

```
┌─────────────────────────────────────────┐
│           MCP Server (FastMCP)          │
│         单一实例，所有工具注册        │
├─────────────────────────────────────────┤
│  Tools (8个)                            │
│  ├── prometheus_query                   │
│  ├── prometheus_query_range             │
│  ├── prometheus_get_targets             │
│  ├── prometheus_get_rules               │
│  ├── prometheus_get_metric_metadata     │
│  ├── prometheus_export_report           │
│  ├── alertmanager_get_alerts            │
│  └── alertmanager_get_silences          │
├─────────────────────────────────────────┤
│  Client Layer                            │
│  └── client.py (PrometheusClient,       │
│                 AlertmanagerClient)      │
└─────────────────────────────────────────┘
```

## 工具规格

### 1. prometheus_query

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL (e.g., http://localhost:9090)
- `query` (string, required): PromQL 查询
- `time` (string, optional): 时间戳

### 2. prometheus_query_range

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL
- `query` (string, required): PromQL 查询
- `start` (string, required): 开始时间
- `end` (string, required): 结束时间
- `step` (string, optional, default="15s"): 步长

### 3. prometheus_get_targets

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL

### 4. prometheus_get_rules

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL

### 5. prometheus_get_metric_metadata

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL
- `metric` (string, optional): 指标名过滤

### 6. prometheus_export_report

**类型**: 只读
**参数**:
- `url` (string, required): Prometheus URL
- `query` (string, required): PromQL 查询
- `start` (string, required): 开始时间
- `end` (string, required): 结束时间
- `step` (string, optional, default="1m"): 步长
- `format` (string, optional, default="json"): "csv" 或 "json"

### 7. alertmanager_get_alerts

**类型**: 只读
**参数**:
- `url` (string, required): Alertmanager URL (e.g., http://localhost:9093)

### 8. alertmanager_get_silences

**类型**: 只读
**参数**:
- `url` (string, required): Alertmanager URL

## API 端点映射

### Prometheus

| 功能 | API 端点 |
|------|----------|
| 即时查询 | GET /api/v1/query |
| 范围查询 | GET /api/v1/query_range |
| Targets | GET /api/v1/targets |
| Rules | GET /api/v1/rules |
| 元数据 | GET /api/v1/metadata |

### Alertmanager

| 功能 | API 端点 |
|------|----------|
| Alarms | GET /api/v2/alerts |
| Silences | GET /api/v2/silences |

## 设计特点

1. **无需配置** - 直接通过 URL 查询，不依赖配置文件
2. **单一实例** - 所有工具注册到同一个 FastMCP 实例
3. **简单直接** - URL 作为必填参数，清晰明了

## 限制

- 不支持修改 Rules 或 Alertmanager 配置（只读）
- 所有 API 调用超时时间: 30s (查询), 60s (范围查询)
