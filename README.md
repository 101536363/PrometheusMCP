# Prometheus MCP

Model Context Protocol (MCP) Server for Prometheus metrics querying.

## 功能

- **直接 URL 查询** - 无需配置，直接通过 URL 查询任意 Prometheus/Alertmanager
- **PromQL 查询** - 即时查询和范围查询
- **Rules 查询** - 查看 Recording Rules 和 Alerting Rules
- **Targets 监控** - 查看抓取目标健康状态
- **Alertmanager** - 查询告警和 Silence 状态
- **报表导出** - 支持 CSV/JSON 格式

## 安装

```bash
pip install -e .
```

## 卸载

```bash
pip uninstall prometheus-mcp
```

## 配置

无需配置！直接通过 URL 查询。

在 OpenCode 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["-m", "prometheus_mcp"]
    }
  }
}
```

## 可用工具

### Prometheus 查询

| 工具 | 说明 |
|------|------|
| `prometheus_query` | PromQL 即时查询 |
| `prometheus_query_range` | PromQL 范围查询 |
| `prometheus_get_targets` | 获取 Targets 状态 |
| `prometheus_get_rules` | 获取所有 Rules |
| `prometheus_get_metric_metadata` | 获取指标元数据 |
| `prometheus_export_report` | 导出报表 (CSV/JSON) |

### Alertmanager 查询

| 工具 | 说明 |
|------|------|
| `alertmanager_get_alerts` | 获取当前告警 |
| `alertmanager_get_silences` | 获取 Silence 列表 |

## 使用示例

### 查询 Prometheus

```python
# 查询 up 指标
prometheus_query(
    url="http://localhost:9090",
    query="up{job='kubernetes-nodes'}"
)

# 范围查询
prometheus_query_range(
    url="http://localhost:9090",
    query="rate(node_cpu_seconds_total[5m])",
    start="2024-01-01T00:00:00Z",
    end="2024-01-02T00:00:00Z",
    step="1m"
)

# 获取 Targets
prometheus_get_targets(url="http://localhost:9090")

# 获取 Rules
prometheus_get_rules(url="http://localhost:9090")
```

### 查询 Alertmanager

```python
# 获取当前告警
alertmanager_get_alerts(url="http://localhost:9093")

# 获取 Silences
alertmanager_get_silences(url="http://localhost:9093")
```

### 导出报表

```python
# 导出 JSON
prometheus_export_report(
    url="http://localhost:9090",
    query="up",
    start="2024-01-01T00:00:00Z",
    end="2024-01-02T00:00:00Z",
    format="json"
)

# 导出 CSV
prometheus_export_report(
    url="http://localhost:9090",
    query="up",
    start="2024-01-01T00:00:00Z",
    end="2024-01-02T00:00:00Z",
    format="csv"
)
```

## 常见查询示例

| 需求 | PromQL |
|------|--------|
| 所有 Pod CPU 排名 | `topk(10, sum by (pod) (rate(container_cpu_usage_seconds_total[5m])))` |
| 所有 Node 内存 | `topk(10, sort_desc(node_memory_MemAvailable_bytes))` |
| Namespace 资源排名 | `topk(10, sum by (namespace) (container_memory_usage_bytes))` |
| 列出所有 Pod | `count by (pod) (kube_pod_info)` |
| 列出所有 Node | `count by (node) (kube_node_info)` |

## 开发

```bash
pip install -e ".[dev]"
```

## 许可证

MIT
