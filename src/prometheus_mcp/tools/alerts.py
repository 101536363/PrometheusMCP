"""Alertmanager query tools."""

import json
import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..config import get_config_manager
from ..client import create_alertmanager_client


mcp = FastMCP("prometheus_mcp")


class AlertsInput(BaseModel):
    """Input for getting alerts."""
    instance: str = Field(default="local", description="Alertmanager instance name from config")


class SilencesInput(BaseModel):
    """Input for getting silences."""
    instance: str = Field(default="local", description="Alertmanager instance name from config")


class AlertmanagerStatusInput(BaseModel):
    """Input for getting Alertmanager status."""
    instance: str = Field(default="local", description="Alertmanager instance name from config")


def _handle_api_error(e: Exception) -> str:
    """Format API errors."""
    if isinstance(e, httpx.HTTPStatusError):
        return json.dumps({"error": f"HTTP {e.response.status_code}", "detail": e.response.text})
    elif isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": "Request timed out"})
    elif isinstance(e, httpx.ConnectError):
        return json.dumps({"error": f"Connection failed: {e}"})
    return json.dumps({"error": f"Unexpected error: {type(e).__name__}", "detail": str(e)})


@mcp.tool(
    name="alertmanager_get_alerts",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_alerts(params: AlertsInput) -> str:
    """Get all active alerts from Alertmanager.

    Args:
        params: Contains Alertmanager instance name from config

    Returns:
        JSON string containing active alerts with labels, annotations, and status.
    """
    config = get_config_manager()
    inst = config.get_alertmanager(params.instance)

    if not inst:
        return json.dumps({"error": f"Alertmanager instance '{params.instance}' not found"})

    try:
        client = create_alertmanager_client(inst)
        result = await client.get_alerts()

        if isinstance(result, list):
            return json.dumps({"status": "success", "data": result}, indent=2)
        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="alertmanager_get_silences",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_silences(params: SilencesInput) -> str:
    """Get all silences from Alertmanager.

    Args:
        params: Contains Alertmanager instance name from config

    Returns:
        JSON string containing silences with matchers, start/end times, and status.
    """
    config = get_config_manager()
    inst = config.get_alertmanager(params.instance)

    if not inst:
        return json.dumps({"error": f"Alertmanager instance '{params.instance}' not found"})

    try:
        client = create_alertmanager_client(inst)
        result = await client.get_silences()

        if isinstance(result, list):
            return json.dumps({"status": "success", "data": result}, indent=2)
        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="alertmanager_get_status",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_alertmanager_status(params: AlertmanagerStatusInput) -> str:
    """Get Alertmanager cluster status and configuration.

    Args:
        params: Contains Alertmanager instance name from config

    Returns:
        JSON string containing Alertmanager status including cluster info.
    """
    config = get_config_manager()
    inst = config.get_alertmanager(params.instance)

    if not inst:
        return json.dumps({"error": f"Alertmanager instance '{params.instance}' not found"})

    try:
        client = create_alertmanager_client(inst)
        result = await client.get_status()

        if result.get("status") == "success":
            return json.dumps(result, indent=2)
        return json.dumps(result, indent=2)

    except Exception as e:
        return _handle_api_error(e)
