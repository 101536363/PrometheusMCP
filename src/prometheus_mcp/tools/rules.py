"""Rules and targets query tools."""

import json
import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..config import get_config_manager
from ..client import create_prometheus_client


mcp = FastMCP("prometheus_mcp")


class TargetsInput(BaseModel):
    """Input for getting targets."""
    instance: str = Field(default="local", description="Prometheus instance name from config")


class RulesInput(BaseModel):
    """Input for getting rules."""
    instance: str = Field(default="local", description="Prometheus instance name from config")


class MetricMetadataInput(BaseModel):
    """Input for getting metric metadata."""
    instance: str = Field(default="local", description="Prometheus instance name from config")
    metric: str = Field(default="", description="Optional metric name filter")


def _handle_api_error(e: Exception) -> str:
    """Format API errors."""
    if isinstance(e, httpx.HTTPStatusError):
        return json.dumps({"error": f"HTTP {e.response.status_code}", "detail": e.response.text})
    elif isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": "Request timed out"})
    return json.dumps({"error": f"Unexpected error: {type(e).__name__}", "detail": str(e)})


@mcp.tool(
    name="prometheus_get_targets",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_targets(params: TargetsInput) -> str:
    """Get all Prometheus scrape targets with their health status.

    Args:
        params: Contains instance name from config

    Returns:
        JSON string containing active and dropped targets with health status.
    """
    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        result = await client.get_targets()

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        return json.dumps({"error": result.get("error", "Failed to get targets")})

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="prometheus_get_rules",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_rules(params: RulesInput) -> str:
    """Get all Prometheus recording and alerting rules.

    Args:
        params: Contains instance name from config

    Returns:
        JSON string containing groups of recording and alerting rules.
    """
    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        result = await client.get_rules()

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        return json.dumps({"error": result.get("error", "Failed to get rules")})

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="prometheus_get_metric_metadata",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_metric_metadata(params: MetricMetadataInput) -> str:
    """Get metadata for Prometheus metrics.

    Args:
        params: Contains instance name and optional metric name filter

    Returns:
        JSON string containing metric metadata including help text and type.
    """
    config = get_config_manager()
    inst = config.get_prometheus(params.instance)

    if not inst:
        return json.dumps({"error": f"Prometheus instance '{params.instance}' not found"})

    try:
        client = create_prometheus_client(inst)
        metric = params.metric if params.metric else None
        result = await client.get_metric_metadata(metric)

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        return json.dumps({"error": result.get("error", "Failed to get metadata")})

    except Exception as e:
        return _handle_api_error(e)
