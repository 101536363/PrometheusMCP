"""HTTP client for Prometheus and Alertmanager APIs."""

import httpx
from typing import Optional, Any
from .config import Instance


class PrometheusClient:
    """HTTP client for Prometheus API."""

    def __init__(self, instance: Instance):
        self.instance = instance
        self.base_url = instance.url.rstrip("/")

    async def query(self, query: str, time: Optional[str] = None) -> dict:
        """Execute an instant query."""
        params = {"query": query}
        if time:
            params["time"] = time

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query",
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def query_range(
        self,
        query: str,
        start: str,
        end: str,
        step: str = "15s"
    ) -> dict:
        """Execute a range query."""
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query_range",
                params=params,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()

    async def get_targets(self) -> dict:
        """Get all targets."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/targets",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_rules(self) -> dict:
        """Get all rules."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/rules",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_metric_metadata(self, metric: Optional[str] = None, limit: int = 10000) -> dict:
        """Get metric metadata."""
        params = {"limit": limit}
        if metric:
            params["metric"] = metric

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/metadata",
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


class AlertmanagerClient:
    """HTTP client for Alertmanager API."""

    def __init__(self, instance: Instance):
        self.instance = instance
        self.base_url = instance.url.rstrip("/")

    async def get_alerts(self) -> dict:
        """Get all alerts."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/alerts",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_silences(self) -> dict:
        """Get all silences."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/silences",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_status(self) -> dict:
        """Get Alertmanager status.

        Note: Alertmanager v2 API doesn't have a direct /status endpoint.
        This endpoint was removed in v0.27.0. We return basic info from /api/v2/alerts.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/alerts",
                timeout=30.0
            )
            response.raise_for_status()
            return {
                "status": "success",
                "data": {
                    "version": "v2",
                    "note": "Alertmanager v2 API - use /api/v2/alerts for alerts"
                }
            }


def create_prometheus_client(instance: Instance) -> PrometheusClient:
    """Create a Prometheus client for the given instance."""
    return PrometheusClient(instance)


def create_alertmanager_client(instance: Instance) -> AlertmanagerClient:
    """Create an Alertmanager client for the given instance."""
    return AlertmanagerClient(instance)
