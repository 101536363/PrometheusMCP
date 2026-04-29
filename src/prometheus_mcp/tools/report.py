"""Report export tools."""

import json
import csv
import io
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..config import get_config_manager
from ..client import create_prometheus_client


mcp = FastMCP("prometheus_mcp")


class ReportFormat(str, Enum):
    """Output format for reports."""
    CSV = "csv"
    JSON = "json"


class ExportReportInput(BaseModel):
    """Input for exporting reports."""
    query: str = Field(..., description="PromQL query string for the report data")
    instance: str = Field(default="local", description="Prometheus instance name from config")
    start: str = Field(..., description="Start time (RFC3339 or Unix timestamp)")
    end: str = Field(..., description="End time (RFC3339 or Unix timestamp)")
    step: str = Field(default="1m", description="Query resolution step")
    format: ReportFormat = Field(default=ReportFormat.JSON, description="Output format: 'csv' or 'json'")


def _handle_api_error(e: Exception) -> str:
    """Format API errors."""
    import httpx
    if isinstance(e, httpx.HTTPStatusError):
        return json.dumps({"error": f"HTTP {e.response.status_code}", "detail": e.response.text})
    elif isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": "Request timed out"})
    return json.dumps({"error": f"Unexpected error: {type(e).__name__}", "detail": str(e)})


def _extract_metric_label(metric: dict) -> tuple[dict, dict]:
    """Extract labels and values from a metric data point."""
    labels = metric.get("metric", {})
    values = []
    if "value" in metric:
        values = [(None, metric["value"])]
    elif "values" in metric:
        values = metric["values"]
    return labels, values


def _format_csv(result: dict) -> str:
    """Format query result as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    if result.get("status") != "success":
        return f"Error: {result.get('error', 'Unknown error')}"

    data = result.get("data", {})
    result_type = data.get("resultType")

    if result_type == "vector":
        writer.writerow(["timestamp", "value"] + [f"label_{k}" for k in sorted(data["result"][0]["metric"].keys())] if data["result"] else ["timestamp", "value"])

        for metric in data["result"]:
            labels = metric.get("metric", {})
            timestamp, value = metric["value"]
            row = [timestamp, value] + [labels.get(k, "") for k in sorted(labels.keys())]
            writer.writerow(row)

    elif result_type == "matrix":
        writer.writerow(["timestamp", "value"] + [f"label_{k}" for k in sorted(data["result"][0]["metric"].keys())] if data["result"] else ["timestamp", "value"])

        for metric in data["result"]:
            labels = metric.get("metric", {})
            for timestamp, value in metric["values"]:
                row = [timestamp, value] + [labels.get(k, "") for k in sorted(labels.keys())]
                writer.writerow(row)

    return output.getvalue()


@mcp.tool(
    name="prometheus_export_report",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def export_report(params: ExportReportInput) -> str:
    """Export PromQL query results as CSV or JSON report.

    This tool executes a range query and exports the results in the specified format.
    Useful for generating reports for further analysis.

    Args:
        params: Contains query, instance, start, end, step, and output format

    Returns:
        CSV or JSON formatted report data.
    """
    import httpx

    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        result = await client.query_range(params.query, params.start, params.end, params.step)

        if result.get("status") != "success":
            return json.dumps({
                "error": result.get("error", "Query failed"),
                "error_type": result.get("errorType")
            })

        if params.format == ReportFormat.CSV:
            return _format_csv(result)
        else:
            output = {
                "query": params.query,
                "instance": params.instance,
                "start": params.start,
                "end": params.end,
                "step": params.step,
                "result_type": result.get("data", {}).get("resultType"),
                "result": result.get("data", {}).get("result"),
                "exported_at": datetime.now().isoformat()
            }
            return json.dumps(output, indent=2)

    except Exception as e:
        return _handle_api_error(e)
