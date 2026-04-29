"""Data models for Prometheus MCP."""

from pydantic import BaseModel, Field
from typing import Optional, Any


class QueryResult(BaseModel):
    """Result from a PromQL query."""
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


class Target(BaseModel):
    """A Prometheus scrape target."""
    scrape_url: str
    labels: dict[str, str]
    health: str
    last_error: Optional[str] = None
    last_scrape: Optional[str] = None


class RuleGroup(BaseModel):
    """A Prometheus rule group."""
    name: str
    file: str
    rules: list[dict]
    interval: Optional[float] = None


class Alert(BaseModel):
    """An alert from Alertmanager."""
    fingerprint: str
    labels: dict[str, str]
    annotations: dict[str, str]
    starts_at: str
    ends_at: Optional[str] = None
    status: str


class Silence(BaseModel):
    """A silence from Alertmanager."""
    id: str
    matchers: list[dict]
    starts_at: str
    ends_at: str
    created_at: str
    created_by: str
    comment: str
    status: str


class InstanceInfo(BaseModel):
    """Information about a configured instance."""
    name: str
    url: str
    type: str  # "prometheus" or "alertmanager"
