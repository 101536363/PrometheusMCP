"""Prometheus MCP Server - Simple URL-based querying.

A Model Context Protocol server for Prometheus metrics querying.
直接通过 URL 查询，无需配置实例。
"""

import json
import csv
import io
import httpx
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from .client import PrometheusClient, AlertmanagerClient


mcp = FastMCP("prometheus_mcp")


class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


class PrometheusQueryInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")
    query: str = Field(..., description="PromQL query string (e.g., 'up{job='kubernetes-nodes'}')")
    time: Optional[str] = Field(default=None, description="Evaluation timestamp (RFC3339 or Unix timestamp)")


class PrometheusQueryRangeInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")
    query: str = Field(..., description="PromQL query string")
    start: str = Field(..., description="Start time (RFC3339 or Unix timestamp)")
    end: str = Field(..., description="End time (RFC3339 or Unix timestamp)")
    step: str = Field(default="15s", description="Query resolution step (e.g., '15s', '1m', '5m')")


class PrometheusTargetsInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")


class PrometheusRulesInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")


class PrometheusMetadataInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")
    metric: str = Field(default="", description="Optional metric name filter")


class PrometheusListMetricsInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")
    limit: int = Field(default=10000, description="Maximum number of metrics to return")


class AlertmanagerAlertsInput(BaseModel):
    url: str = Field(..., description="Alertmanager URL (e.g., http://localhost:9093)")


class AlertmanagerSilencesInput(BaseModel):
    url: str = Field(..., description="Alertmanager URL (e.g., http://localhost:9093)")


class ExportReportInput(BaseModel):
    url: str = Field(..., description="Prometheus URL (e.g., http://localhost:9090)")
    query: str = Field(..., description="PromQL query string for the report data")
    start: str = Field(..., description="Start time (RFC3339 or Unix timestamp)")
    end: str = Field(..., description="End time (RFC3339 or Unix timestamp)")
    step: str = Field(default="1m", description="Query resolution step")
    format: ReportFormat = Field(default=ReportFormat.JSON, description="Output format: 'csv' or 'json'")


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        return json.dumps({"error": f"HTTP {e.response.status_code}", "detail": e.response.text[:200]})
    elif isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": "Request timed out"})
    elif isinstance(e, httpx.ConnectError):
        return json.dumps({"error": f"Connection failed: {e}"})
    return json.dumps({"error": f"Unexpected error: {type(e).__name__}", "detail": str(e)[:200]})


def _format_csv(result: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    if result.get("status") != "success":
        return f"Error: {result.get('error', 'Unknown error')}"

    data = result.get("data", {})
    result_type = data.get("resultType")

    if result_type == "vector":
        headers = ["timestamp", "value"]
        if data["result"]:
            headers.extend([f"label_{k}" for k in sorted(data["result"][0]["metric"].keys())])
        writer.writerow(headers)

        for metric in data["result"]:
            labels = metric.get("metric", {})
            timestamp, value = metric["value"]
            row = [timestamp, value] + [labels.get(k, "") for k in sorted(labels.keys())]
            writer.writerow(row)

    elif result_type == "matrix":
        headers = ["timestamp", "value"]
        if data["result"]:
            headers.extend([f"label_{k}" for k in sorted(data["result"][0]["metric"].keys())])
        writer.writerow(headers)

        for metric in data["result"]:
            labels = metric.get("metric", {})
            for timestamp, value in metric["values"]:
                row = [timestamp, value] + [labels.get(k, "") for k in sorted(labels.keys())]
                writer.writerow(row)

    return output.getvalue()


@mcp.tool()
async def prometheus_query(params: PrometheusQueryInput) -> str:
    """Execute an instant PromQL query at a single point in time.

    Args:
        params: Contains url (Prometheus endpoint) and query (PromQL string)

    Returns:
        JSON string containing query results with status and metric data.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.query(params.query, params.time)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_query_range(params: PrometheusQueryRangeInput) -> str:
    """Execute a PromQL range query over a time range.

    Args:
        params: Contains url, query, start, end, and step for range query

    Returns:
        JSON string containing range query results with time series data.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.query_range(params.query, params.start, params.end, params.step)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_get_targets(params: PrometheusTargetsInput) -> str:
    """Get all Prometheus scrape targets with their health status.

    Args:
        params: Contains url (Prometheus endpoint)

    Returns:
        JSON string containing active and dropped targets with health status.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.get_targets()
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_get_rules(params: PrometheusRulesInput) -> str:
    """Get all Prometheus recording and alerting rules.

    Args:
        params: Contains url (Prometheus endpoint)

    Returns:
        JSON string containing groups of recording and alerting rules.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.get_rules()
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_get_metric_metadata(params: PrometheusMetadataInput) -> str:
    """Get metadata for Prometheus metrics.

    Args:
        params: Contains url and optional metric name filter

    Returns:
        JSON string containing metric metadata including help text and type.
    """
    try:
        client = PrometheusClient(params.url)
        metric = params.metric if params.metric else None
        result = await client.get_metric_metadata(metric)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_list_metrics(params: PrometheusListMetricsInput) -> str:
    """List all available metric names in Prometheus.

    This tool discovers all metric names available in Prometheus.
    Useful for exploring what metrics are available before writing queries.

    Args:
        params: Contains url and limit (max number of metrics)

    Returns:
        JSON string containing list of all available metric names.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.list_metrics(params.limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def alertmanager_get_alerts(params: AlertmanagerAlertsInput) -> str:
    """Get all active alerts from Alertmanager.

    Args:
        params: Contains url (Alertmanager endpoint)

    Returns:
        JSON string containing active alerts with labels, annotations, and status.
    """
    try:
        client = AlertmanagerClient(params.url)
        result = await client.get_alerts()
        if isinstance(result, list):
            return json.dumps({"status": "success", "data": result}, indent=2)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def alertmanager_get_silences(params: AlertmanagerSilencesInput) -> str:
    """Get all silences from Alertmanager.

    Args:
        params: Contains url (Alertmanager endpoint)

    Returns:
        JSON string containing silences with matchers, start/end times, and status.
    """
    try:
        client = AlertmanagerClient(params.url)
        result = await client.get_silences()
        if isinstance(result, list):
            return json.dumps({"status": "success", "data": result}, indent=2)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool()
async def prometheus_export_report(params: ExportReportInput) -> str:
    """Export PromQL query results as CSV or JSON report.

    Args:
        params: Contains url, query, start, end, step, and output format

    Returns:
        CSV or JSON formatted report data.
    """
    try:
        client = PrometheusClient(params.url)
        result = await client.query_range(params.query, params.start, params.end, params.step)

        if result.get("status") != "success":
            return json.dumps({"error": result.get("error", "Query failed")})

        if params.format == ReportFormat.CSV:
            return _format_csv(result)
        else:
            return json.dumps({
                "query": params.query,
                "url": params.url,
                "start": params.start,
                "end": params.end,
                "step": params.step,
                "result_type": result.get("data", {}).get("resultType"),
                "result": result.get("data", {}).get("result"),
            }, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
