"""Instance management tools."""

import json
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..config import get_config_manager
from ..models import InstanceInfo


mcp = FastMCP("prometheus_mcp")


class InstanceType(str):
    """Instance type enum."""
    PROMETHEUS = "prometheus"
    ALERTMANAGER = "alertmanager"


class ListPrometheusInput(BaseModel):
    """Input for listing Prometheus instances."""
    pass


class ListAlertmanagerInput(BaseModel):
    """Input for listing Alertmanager instances."""
    pass


class AddInstanceInput(BaseModel):
    """Input for adding an instance."""
    name: str = Field(..., description="Unique name for the instance", min_length=1)
    url: str = Field(..., description="Base URL of the instance (e.g., http://localhost:9090)")
    type: str = Field(..., description="Instance type: 'prometheus' or 'alertmanager'")


class RemoveInstanceInput(BaseModel):
    """Input for removing an instance."""
    name: str = Field(..., description="Name of the instance to remove")
    type: str = Field(..., description="Instance type: 'prometheus' or 'alertmanager'")


@mcp.tool(
    name="prometheus_list_instances",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_prometheus_instances() -> str:
    """List all configured Prometheus instances.

    Returns:
        JSON string containing list of Prometheus instances with name and URL.
    """
    config = get_config_manager()
    instances = config.list_prometheus()

    result = {
        "count": len(instances),
        "instances": [
            {"name": inst.name, "url": inst.url}
            for inst in instances
        ]
    }
    return json.dumps(result, indent=2)


@mcp.tool(
    name="alertmanager_list_instances",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_alertmanager_instances() -> str:
    """List all configured Alertmanager instances.

    Returns:
        JSON string containing list of Alertmanager instances with name and URL.
    """
    config = get_config_manager()
    instances = config.list_alertmanager()

    result = {
        "count": len(instances),
        "instances": [
            {"name": inst.name, "url": inst.url}
            for inst in instances
        ]
    }
    return json.dumps(result, indent=2)


@mcp.tool(
    name="prometheus_add_instance",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def add_instance(params: AddInstanceInput) -> str:
    """Add a Prometheus or Alertmanager instance to the configuration.

    Args:
        params: Contains name (unique identifier), url (base URL), and type (prometheus/alertmanager)

    Returns:
        JSON string confirming the added instance.
    """
    config = get_config_manager()

    try:
        if params.type.lower() == "prometheus":
            inst = config.add_prometheus(params.name, params.url)
            result = {"success": True, "type": "prometheus", "name": inst.name, "url": inst.url}
        elif params.type.lower() == "alertmanager":
            inst = config.add_alertmanager(params.name, params.url)
            result = {"success": True, "type": "alertmanager", "name": inst.name, "url": inst.url}
        else:
            return json.dumps({"error": f"Invalid type '{params.type}'. Must be 'prometheus' or 'alertmanager'"})

        return json.dumps(result, indent=2)
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="prometheus_remove_instance",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def remove_instance(params: RemoveInstanceInput) -> str:
    """Remove a Prometheus or Alertmanager instance from the configuration.

    Args:
        params: Contains name and type (prometheus/alertmanager) of instance to remove

    Returns:
        JSON string confirming removal or error if not found.
    """
    config = get_config_manager()

    if params.type.lower() == "prometheus":
        success = config.remove_prometheus(params.name)
        if success:
            return json.dumps({"success": True, "type": "prometheus", "name": params.name, "removed": True})
        return json.dumps({"error": f"Prometheus instance '{params.name}' not found"})

    elif params.type.lower() == "alertmanager":
        success = config.remove_alertmanager(params.name)
        if success:
            return json.dumps({"success": True, "type": "alertmanager", "name": params.name, "removed": True})
        return json.dumps({"error": f"Alertmanager instance '{params.name}' not found"})

    return json.dumps({"error": f"Invalid type '{params.type}'. Must be 'prometheus' or 'alertmanager'"})
