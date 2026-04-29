"""HTTP client for Prometheus and Alertmanager APIs."""

import httpx
from typing import Optional


class PrometheusClient:
    """HTTP client for Prometheus API."""

    def __init__(self, url: str):
        self.base_url = url.rstrip("/")

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

    async def list_metrics(self, limit: int = 10000) -> dict:
        """List all available metric names."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/label/__name__/values",
                params={"limit": limit},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


class AlertmanagerClient:
    """HTTP client for Alertmanager API."""

    def __init__(self, url: str):
        self.base_url = url.rstrip("/")

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
