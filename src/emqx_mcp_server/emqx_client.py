"""
EMQX HTTP API Client Module

This module provides a client for interacting with the EMQX MQTT broker's HTTP API.
It handles authentication, request formatting, and response processing.
"""

import base64
import logging
from json import JSONDecodeError

import httpx

from .config import EMQX_API_KEY, EMQX_API_SECRET, EMQX_API_URL


class EMQXClient:
    """
    EMQX HTTP API Client

    Provides methods to interact with EMQX Cloud or self-hosted EMQX broker
    through its HTTP API. Handles authentication and error processing.

    Attributes:
        api_url (str): The base URL for the EMQX HTTP API
        api_key (str): API key for authentication
        api_secret (str): API secret for authentication
        logger (Logger): Logger instance for logging messages
    """

    def __init__(self, logger: logging.Logger):
        self.api_url = EMQX_API_URL
        self.api_key = EMQX_API_KEY
        self.api_secret = EMQX_API_SECRET
        self.logger = logger

    async def get(self, path: str, **kwargs):
        """Get request"""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        """Post request"""
        return await self._request("POST", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        """Delete request"""
        return await self._request("DELETE", path, **kwargs)

    async def put(self, path: str, **kwargs):
        """Put request"""
        return await self._request("PUT", path, **kwargs)

    def _get_auth_header(self):
        """Create authorization header for EMQX Cloud API"""
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
        }

    def _handle_response(self, response):
        """Process API response, extract data and handle errors"""
        try:
            result = response.json()
            if response.status_code >= 200 and response.status_code < 300:
                return {"result": result}
            else:
                error_msg = result.get("message", "Unknown error")
                self.logger.info(f"EMQX API Error: {response.status_code} - {error_msg}")
                return {"error": error_msg}
        except JSONDecodeError:
            response.raise_for_status()

    async def _request(self, method: str, path: str, **kwargs):
        """Send HTTP request to EMQX API"""
        url = f"{self.api_url}/{path}"
        headers = self._get_auth_header()
        kwargs["headers"] = headers
        kwargs["timeout"] = 30
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, **kwargs)
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error sending request: {str(e)}")
                return {"error": str(e)}

