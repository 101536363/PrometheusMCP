"""Prometheus query tools."""

import json
import httpx
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..config import get_config_manager
from ..client import create_prometheus_client


mcp = FastMCP("prometheus_mcp")


class QueryInput(BaseModel):
    """Input for instant query."""
    query: str = Field(..., description="PromQL query string (e.g., 'up{job=\"kubernetes-nodes\"}')")
    instance: str = Field(default="local", description="Prometheus instance name from config")
    time: Optional[str] = Field(default=None, description="Evaluation timestamp (RFC3339 or Unix timestamp)")


class QueryRangeInput(BaseModel):
    """Input for range query."""
    query: str = Field(..., description="PromQL query string")
    instance: str = Field(default="local", description="Prometheus instance name from config")
    start: str = Field(..., description="Start time (RFC3339 or Unix timestamp)")
    end: str = Field(..., description="End time (RFC3339 or Unix timestamp)")
    step: str = Field(default="15s", description="Query resolution step (e.g., '15s', '1m', '5m')")


def _handle_api_error(e: Exception) -> str:
    """Format API errors."""
    if isinstance(e, httpx.HTTPStatusError):
        return json.dumps({
            "error": f"HTTP {e.response.status_code}",
            "detail": e.response.text
        })
    elif isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": "Request timed out"})
    elif isinstance(e, httpx.ConnectError):
        return json.dumps({"error": f"Connection failed: {e}"})
    return json.dumps({"error": f"Unexpected error: {type(e).__name__}", "detail": str(e)})


@mcp.tool(
    name="prometheus_query",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def query(params: QueryInput) -> str:
    """Execute an instant PromQL query at a single point in time.

    Args:
        params: Contains query (PromQL string), instance (name from config), and optional time

    Returns:
        JSON string containing query results with status and metric data.
    """
    import httpx

    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        result = await client.query(params.query, params.time)

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        else:
            return json.dumps({
                "error": result.get("error", "Query failed"),
                "error_type": result.get("errorType")
            })

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="prometheus_query_range",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def query_range(params: QueryRangeInput) -> str:
    """Execute a PromQL range query over a time range.

    Args:
        params: Contains query, instance, start, end, and step for range query

    Returns:
        JSON string containing range query results with time series data.
    """
    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        result = await client.query_range(params.query, params.start, params.end, params.step)

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        else:
            return json.dumps({
                "error": result.get("error", "Query failed"),
                "error_type": result.get("errorType")
            })

    except Exception as e:
        return _handle_api_error(e)
