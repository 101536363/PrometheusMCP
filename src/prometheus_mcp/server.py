"""Prometheus MCP Server.

A Model Context Protocol server for Prometheus metrics querying and management.
"""

from .tools.instances import mcp as instances_mcp
from .tools.query import mcp as query_mcp
from .tools.rules import mcp as rules_mcp
from .tools.alerts import mcp as alerts_mcp
from .tools.report import mcp as report_mcp


def create_server():
    """Create and configure the MCP server with all tools."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("prometheus_mcp")

    for tool_mcp in [instances_mcp, query_mcp, rules_mcp, alerts_mcp, report_mcp]:
        for name, func in tool_mcp._tool_manager._tools.items():
            server._tool_manager._tools[name] = func

    return server


def main():
    """Run the MCP server."""
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
