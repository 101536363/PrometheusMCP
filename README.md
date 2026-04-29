# Prometheus MCP

Model Context Protocol (MCP) Server for Prometheus metrics querying and management.

## 功能

- **多实例管理** - 通过 YAML 配置管理多个 Prometheus/Alertmanager 实例
- **指标查询** - PromQL 即时查询和范围查询
- **Rules 查询** - 查看 Recording Rules 和 Alerting Rules
- **Targets 监控** - 查看抓取目标健康状态
- **Alertmanager** - 查询告警和 Silence 状态
- **报表导出** - 支持 CSV/JSON 格式

## 安装

```bash
pip install -e .
```

## 配置

创建 `instances.yaml` 文件：

```yaml
prometheus:
  - name: prod
    url: http://prometheus:9090
  - name: dev
    url: http://dev-prometheus:9090

alertmanager:
  - name: prod-am
    url: http://alertmanager:9093
```

## 使用方法

### OpenCode 配置

在 OpenCode 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["-m", "prometheus_mcp"],
      "env": {
        "PROMETHEUS_CONFIG": "./instances.yaml"
      }
    }
  }
}
```

### 可用工具

| 工具 | 说明 |
|------|------|
| `prometheus_list_instances` | 列出所有 Prometheus 实例 |
| `alertmanager_list_instances` | 列出所有 Alertmanager 实例 |
| `prometheus_add_instance` | 添加新实例 |
| `prometheus_remove_instance` | 删除实例 |
| `prometheus_query` | PromQL 即时查询 |
| `prometheus_query_range` | PromQL 范围查询 |
| `prometheus_get_targets` | 获取 Targets 状态 |
| `prometheus_get_rules` | 获取所有 Rules |
| `prometheus_get_metric_metadata` | 获取指标元数据 |
| `alertmanager_get_alerts` | 获取当前告警 |
| `alertmanager_get_silences` | 获取 Silence 列表 |
| `alertmanager_get_status` | 获取 Alertmanager 状态 |
| `prometheus_export_report` | 导出报表 (CSV/JSON) |

### 示例查询

```python
# 查询 up 指标
prometheus_query(query="up{job='kubernetes-nodes'}")

# 范围查询
prometheus_query_range(
    query="rate(node_cpu_seconds_total[5m])",
    start="2024-01-01T00:00:00Z",
    end="2024-01-02T00:00:00Z",
    step="1m"
)

# 导出报表
prometheus_export_report(
    query="up",
    start="2024-01-01T00:00:00Z",
    end="2024-01-02T00:00:00Z",
    format="csv"
)
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## 许可证

MIT
