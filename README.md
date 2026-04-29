# Prometheus MCP

Model Context Protocol (MCP) Server for Prometheus metrics querying.

## 功能

- **直接 URL 查询** - 无需配置，直接通过 URL 查询任意 Prometheus/Alertmanager
- **PromQL 查询** - 即时查询和范围查询
- **指标发现** - 列出所有可用的指标名称
- **Rules 查询** - 查看 Recording Rules 和 Alerting Rules
- **Targets 监控** - 查看抓取目标健康状态
- **Alertmanager** - 查询告警和 Silence 状态
- **报表导出** - 支持 CSV/JSON 格式

---

## 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.10 - 3.14 |
| pip | 最新版 |

### 检查 Python 版本

```bash
python3 --version
# 应显示 Python 3.10.x 或更高
```

---

## 部署方式 A: 本机安装（pip）

### 1. 克隆代码

```bash
git clone <repo-url>
cd prometheus-mcp
```

### 2. 安装

```bash
pip3 install -e .
```

### 3. 验证安装

```bash
python3 -m prometheus_mcp
# 无输出表示正常运行（按 Ctrl+C 停止）
```

### 4. 卸载

```bash
pip3 uninstall prometheus-mcp
```

---

## 部署方式 B: Docker

### 前置条件

- Docker 已安装

### 1. 克隆代码

```bash
git clone <repo-url>
cd prometheus-mcp
```

### 2. 构建镜像（不启动）

```bash
docker build -t prometheus-mcp .
```

### 3. 运行（可选）

```bash
docker run prometheus-mcp
```

---

## OpenCode 配置

在 OpenCode 的配置文件中添加：

```json
{
  "mcp": {
    "prometheus": {
      "type": "local",
      "command": ["/Library/Frameworks/Python.framework/Versions/3.14/bin/python3", "-m", "prometheus_mcp"],
      "enabled": true
    }
  }
}
```

**注意**：将 `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` 替换为你的 Python 路径。

### 检查 Python 路径

```bash
which python3
```

---

## 可用工具（共 9 个）

### Prometheus 查询

| 工具 | 说明 |
|------|------|
| `prometheus_query` | PromQL 即时查询 |
| `prometheus_query_range` | PromQL 范围查询 |
| `prometheus_list_metrics` | 列出所有可用指标 |
| `prometheus_get_targets` | 获取 Targets 状态 |
| `prometheus_get_rules` | 获取所有 Rules |
| `prometheus_get_metric_metadata` | 获取指标元数据 |
| `prometheus_export_report` | 导出报表 (CSV/JSON) |

### Alertmanager 查询

| 工具 | 说明 |
|------|------|
| `alertmanager_get_alerts` | 获取当前告警 |
| `alertmanager_get_silences` | 获取 Silence 列表 |

---

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

# 列出所有指标
prometheus_list_metrics(url="http://localhost:9090")

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

---

## 常见查询示例

| 需求 | PromQL |
|------|--------|
| 所有 Pod CPU 排名 | `topk(10, sum by (pod) (rate(container_cpu_usage_seconds_total[5m])))` |
| 所有 Node 内存 | `topk(10, sort_desc(node_memory_MemAvailable_bytes))` |
| Namespace 资源排名 | `topk(10, sum by (namespace) (container_memory_usage_bytes))` |
| 列出所有 Pod | `count by (pod) (kube_pod_info)` |
| 列出所有 Node | `count by (node) (kube_node_info)` |

---

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

---

## 许可证

MIT
