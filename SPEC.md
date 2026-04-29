# Prometheus MCP 规格文档

## 项目概述

- **项目名称**: prometheus-mcp
- **类型**: MCP Server (Model Context Protocol)
- **功能**: Prometheus/Alertmanager API 封装，提供标准化工具接口
- **技术栈**: Python 3.10+, FastMCP, httpx, Pydantic

## 架构

```
┌─────────────────────────────────────────┐
│           MCP Server                    │
│         (FastMCP)                      │
├─────────────────────────────────────────┤
│  Tools Layer                            │
│  ├── instances.py  - 实例管理            │
│  ├── query.py      - 查询工具            │
│  ├── rules.py      - Rules/Targets      │
│  ├── alerts.py     - Alertmanager       │
│  └── report.py     - 报表导出           │
├─────────────────────────────────────────┤
│  Client Layer                            │
│  └── client.py     - HTTP 客户端        │
├─────────────────────────────────────────┤
│  Config Layer                            │
│  └── config.py     - YAML 配置管理      │
└─────────────────────────────────────────┘
```

## 配置格式

```yaml
prometheus:
  - name: <string>   # 实例名称（唯一标识）
    url: <string>   # Base URL

alertmanager:
  - name: <string>
    url: <string>
```

## 工具规格

### 1. prometheus_list_instances

**类型**: 只读
**参数**: 无
**返回**: 所有配置的 Prometheus 实例列表

### 2. alertmanager_list_instances

**类型**: 只读
**参数**: 无
**返回**: 所有配置的 Alertmanager 实例列表

### 3. prometheus_add_instance

**类型**: 写
**参数**:
- `name` (string, required): 实例名称
- `url` (string, required): Base URL
- `type` (string, required): "prometheus" 或 "alertmanager"

### 4. prometheus_remove_instance

**类型**: 删除
**参数**:
- `name` (string, required): 实例名称
- `type` (string, required): "prometheus" 或 "alertmanager"

### 5. prometheus_query

**类型**: 只读
**参数**:
- `query` (string, required): PromQL 查询
- `instance` (string, optional, default="local"): 实例名称
- `time` (string, optional): 时间戳 (RFC3339 或 Unix)

**返回**: 查询结果 (JSON)

### 6. prometheus_query_range

**类型**: 只读
**参数**:
- `query` (string, required): PromQL 查询
- `instance` (string, optional): 实例名称
- `start` (string, required): 开始时间
- `end` (string, required): 结束时间
- `step` (string, optional, default="15s"): 步长

### 7. prometheus_get_targets

**类型**: 只读
**参数**:
- `instance` (string, optional): 实例名称

**返回**: 所有 scrape targets 及其健康状态

### 8. prometheus_get_rules

**类型**: 只读
**参数**:
- `instance` (string, optional): 实例名称

**返回**: 所有 Recording 和 Alerting rules

### 9. alertmanager_get_alerts

**类型**: 只读
**参数**:
- `instance` (string, optional): 实例名称

**返回**: 所有 firing/pending 告警

### 10. alertmanager_get_silences

**类型**: 只读
**参数**:
- `instance` (string, optional): 实例名称

**返回**: 所有 silences 及其状态

### 11. prometheus_export_report

**类型**: 只读
**参数**:
- `query` (string, required): PromQL 查询
- `instance` (string, optional): 实例名称
- `start` (string, required): 开始时间
- `end` (string, required): 结束时间
- `step` (string, optional, default="1m"): 步长
- `format` (string, optional, default="json"): "csv" 或 "json"

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
| Status | GET /api/v1/status |

## 错误处理

所有工具返回统一错误格式:

```json
{
  "error": "错误描述",
  "detail": "详细信息（可选）"
}
```

## 限制

- 不支持修改 Rules 或 Alertmanager 配置（只读）
- 不支持告警/Silence 的创建、修改、删除操作
- 所有 API 调用超时时间: 30s (查询), 60s (范围查询)
