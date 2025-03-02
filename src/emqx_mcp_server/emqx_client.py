"""
EMQX HTTP API Client Module

This module provides a client for interacting with the EMQX MQTT broker's HTTP API.
It handles authentication, request formatting, and response processing.
"""

import httpx
import base64
import logging
from .config import EMQX_API_URL, EMQX_API_KEY, EMQX_API_SECRET

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
        
    def _get_auth_header(self):
        """Create authorization header for EMQX Cloud API"""
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response):
        """Process API response, extract data and handle errors"""
        try:
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            else:
                error_msg = f"EMQX API Error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    async def publish_message(self, topic: str, payload: str, qos: int=0, retain: bool=False):
        """
        Publish a message to an MQTT topic.
        
        Uses the EMQX HTTP API to publish a message to a specific MQTT topic.
        
        Args:
            topic (str): The MQTT topic to publish to
            payload (str): The message payload to publish
            qos (int, optional): Quality of Service level (0, 1, or 2). Defaults to 0.
            retain (bool, optional): Whether to retain the message. Defaults to False.
            
        Returns:
            dict: Response from the EMQX API or error information
        """
        url = f"{self.api_url}/publish"
        data = {
            "topic": topic,
            "payload": payload,
            "qos": qos,
            "retain": retain
        }
        self.logger.info(f"Publishing message to topic {topic}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self._get_auth_header(), json=data, timeout=30)
                response.raise_for_status()
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error publishing message: {str(e)}")
                return {"error": str(e)}