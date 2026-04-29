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

OpenCode 配置

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



---

## 部署方式 B: Docker

### 前置条件

- Docker 已安装

### 方式 1: 直接使用预构建镜像（推荐）

```bash
docker run -d --name prometheus-mcp 101536363/prometheus_mcp:latest
```

OpenCode 配置：
```json
{
  "mcp": {
    "prometheus": {
      "type": "local",
      "command": ["docker", "run", "-i", "--rm", "101536363/prometheus_mcp:latest"],
      "enabled": true
    }
  }
}
```

### 方式 2: 自行构建镜像

```bash
git clone <repo-url>
cd prometheus-mcp
docker build -t prometheus-mcp .
```

OpenCode 配置：
```json
{
  "mcp": {
    "prometheus": {
      "type": "local",
      "command": ["docker", "run", "-i", "--rm", "prometheus-mcp"],
      "enabled": true
    }
  }
}
```

---

## 方式 3: kubectl proxy 场景配置

当你使用 `kubectl port-forward` 将 K8s 集群内的 Prometheus 端口映射到本地时，Docker 容器无法直接访问 `localhost:9090`。需要使用以下配置：

```json
{
  "mcp": {
    "prometheus": {
      "type": "local",
      "command": ["docker", "run", "-i", "--rm", "--add-host=host.docker.internal:host-gateway", "101536363/prometheus_mcp:latest"],
      "enabled": true
    }
  }
}
```

### 原理说明

| 地址 | 含义 |
|------|------|
| `localhost:9090` | Docker 容器内部的 localhost（访问不到宿主机） |
| `host.docker.internal:9090` | 宿主机（macOS/Windows）的 localhost |

`--add-host=host.docker.internal:host-gateway` 让容器内可以解析到宿主机的 IP，从而访问宿主机上 kubectl port-forward 映射的 Prometheus。

### 使用方式

配置完成后，查询时指定 `host.docker.internal:9090` 作为 URL：

> "用 host.docker.internal:9090 查询 up"

> 注意：`host.docker.internal` 仅支持 Docker Desktop for Mac/Windows。Linux 用户请使用 [方案 B（二进制安装）](#部署方式-a-本机安装pip)。

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

### kubectl proxy 场景查询

当你通过 kubectl port-forward 访问 Prometheus 时：

```python
# 查询 up 指标
prometheus_query(
    url="http://host.docker.internal:9090",
    query="up{job='MyHomeLab-SerV'}"
)

# 获取告警规则
prometheus_get_rules(url="http://host.docker.internal:9090")
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

---

## 效果展示

### 自然语言查询

![自然语言查询](image/1.png)

### 查询结果

![查询结果](image/2.png)
