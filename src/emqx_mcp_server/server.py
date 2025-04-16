"""
EMQX MCP Server

This module provides the EMQX MCP Server for any MCP Clients to connect to and interact with
EMQX MQTT broker through its HTTP API. It sets up a FastMCP server that registers EMQX-specific
tools for clients to use.
"""

import logging

from mcp.server.fastmcp import FastMCP

from .tools.emqx_client_tools import EMQXClientTools
from .tools.emqx_message_tools import EMQXMessageTools
from .tools.emqx_rule_tools import EMQXRuleTools


class EMQXMCPServer:
    """
    EMQX MCP Server

    This class initializes the EMQX MCP Server and registers the necessary tools.
    """
    def __init__(self):
        """
        Initialize the EMQX MCP Server.
        
        Sets up the FastMCP server, configures logging, and registers the necessary tools.
        """
        self.name = "emqx_mcp_server"
        self.mcp = FastMCP("emqx_mcp_server")

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)

        # Register tools for client usage
        self._register_tools()

    def _register_tools(self):
        # Register message tools
        emqx_message_tools = EMQXMessageTools(self.logger)
        emqx_message_tools.register_tools(self.mcp)
        self.logger.info("EMQX message tools registered")

        # Register client tools
        emqx_client_tools = EMQXClientTools(self.logger)
        emqx_client_tools.register_tools(self.mcp)
        self.logger.info("EMQX client tools registered")

        # Register rule tools
        emqx_rule_tools = EMQXRuleTools(self.logger)
        emqx_rule_tools.register_tools(self.mcp)
        self.logger.info("EMQX rule tools registered")

    def run(self):
        self.logger.info("Starting EMQX MCP Server")
        self.mcp.run()