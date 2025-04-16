"""
EMQX Rule Tools Module

This module provides tools for helping with composing SQL for
EMQX Rule Engine.
"""

import logging
from typing import Any, Literal, TypedDict

from ..emqx_client import EMQXClient


class ErrorResult(TypedDict):
    error: str

class SuccessResult(TypedDict):
    result: dict[str, Any] | list[Any]


class RulePublishContext(TypedDict):
    event: Literal["message.publish"]
    event_type: Literal["message_publish"]
    id: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    publish_received_at: int
    qos: int


class RuleSubscribeContext(TypedDict):
    event: Literal["session.subscribed"]
    event_type: Literal["session_subscribed"]
    id: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleUnsubscribeContext(TypedDict):
    event: Literal["session.unsubscribed"]
    event_type: Literal["session_unsubscribed"]
    id: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleDeliveredContext(TypedDict):
    event: Literal["message.delivered"]
    event_type: Literal["message_delivered"]
    id: str
    from_clientid: str
    from_username: str | None
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleAckedContext(TypedDict):
    event: Literal["message.acked"]
    event_type: Literal["message_acked"]
    id: str
    from_clientid: str
    from_username: str | None
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleDroppedContext(TypedDict):
    event: Literal["message.dropped"]
    event_type: Literal["message_dropped"]
    id: str
    reason: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleConnectedContext(TypedDict):
    event: Literal["client.connected"]
    event_type: Literal["client_connected"]
    clientid: str
    username: str | None
    mountpoint: str
    peername: str
    sockname: str
    proto_name: str
    proto_ver: str
    keepalive: int
    clean_start: bool
    expiry_interval: int
    is_bridge: bool
    connected_at: int


class RuleDisconnectedContext(TypedDict):
    event: Literal["client.disconnected"]
    event_type: Literal["client_disconnected"]
    clientid: str
    username: str | None
    reason: str
    peername: str
    sockname: str
    disconnected_at: int


class RuleConnackContext(TypedDict):
    event: Literal["client.connack"]
    event_type: Literal["client_connack"]
    reason_code: str
    clientid: str
    clean_start: bool
    username: str | None
    peername: str
    sockname: str
    proto_name: str
    proto_ver: str
    keepalive: int
    expiry_interval: int
    connected_at: int


class RuleCheckAuthzCompleteContext(TypedDict):
    event: Literal["client.check_authz_complete"]
    event_type: Literal["client_check_authz_complete"]
    clientid: str
    username: str | None
    peerhost: str
    topic: str
    action: str
    authz_source: str
    result: str


class RuleCheckAuthnCompleteContext(TypedDict):
    event: Literal["client.check_authn_complete"]
    event_type: Literal["client_check_authn_complete"]
    clientid: str
    username: str | None
    reason_code: str
    peername: str
    is_anonymous: bool | None
    is_superuser: bool | None


class RuleBridgeMqttContext(TypedDict):
    event: str
    event_type: str
    id: str
    payload: str
    topic: str
    server: str
    dup: str
    retain: str
    message_received_at: int
    qos: int


class RuleDeliveryDroppedContext(TypedDict):
    event: Literal["delivery.dropped"]
    event_type: Literal["delivery_dropped"]
    id: str
    reason: str
    from_clientid: str
    from_username: str | None
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleSchemaValidationFailedContext(TypedDict):
    event: Literal["schema.validation_failed"]
    event_type: Literal["schema_validation_failed"]
    validation: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleMessageTransformationFailedContext(TypedDict):
    event: Literal["message.transformation_failed"]
    event_type: Literal["message_transformation_failed"]
    transformation: str
    clientid: str
    username: str | None
    payload: str
    peerhost: str
    topic: str
    qos: int


class RuleAlarmActivatedContext(TypedDict):
    event: Literal["alarm.activated"]
    event_type: Literal["alarm_activated"]
    name: str
    message: str
    details: dict[str, Any]
    activated_at: int


class RuleAlarmDeactivatedContext(TypedDict):
    event: Literal["alarm.deactivated"]
    event_type: Literal["alarm_deactivated"]
    name: str
    message: str
    details: dict[str, Any]
    activated_at: int
    deactivated_at: int


class ValidateRuleSQLRequest(TypedDict):
    sql: str
    context: (
        RulePublishContext
        | RuleSubscribeContext
        | RuleUnsubscribeContext
        | RuleDeliveredContext
        | RuleAckedContext
        | RuleDroppedContext
        | RuleConnectedContext
        | RuleDisconnectedContext
        | RuleConnackContext
        | RuleCheckAuthzCompleteContext
        | RuleCheckAuthnCompleteContext
        | RuleBridgeMqttContext
        | RuleDeliveryDroppedContext
        | RuleSchemaValidationFailedContext
        | RuleMessageTransformationFailedContext
        | RuleAlarmActivatedContext
        | RuleAlarmDeactivatedContext
    )

class SchemaRegistryEntry(TypedDict):
    name: str
    description: str


class EMQXRuleTools:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.emqx_client = EMQXClient(logger)

    def register_tools(self, mcp: Any):
        """Register EMQX Rule Engine tools."""

        @mcp.tool()
        async def validate_sql(request: ValidateRuleSQLRequest) -> SuccessResult | ErrorResult:
            """Validate an SQL statement for the EMQX Rule Engine

            Args:
                request: request containing SQL statement and context for testing the rule SQL:
                    - sql: SQL statement to validate
                    - context: Context for testing the rule SQL. Context contains sample data to be
                               handled by the rule SQL.

            Returns:
                result: a map with successful result or with a error message
            """

            # Extract parameters from the request
            if "sql" not in request:
                return {"error": "Missing required parameter: sql"}

            if "context" not in request:
                return {"error": "Missing required parameter: context"}

            sql = request.get("sql")
            context = request.get("context")

            self.logger.info(f"Validating SQL: {sql}")
            self.logger.info(f"Context: {context}")

            # Test rule SQL using the client
            result = await self.emqx_client.post(
                "rule_test",
                json={"sql": sql, "context": context},
            )
            self.logger.info(f"Validation result: {result}")
            return result

        @mcp.tool()
        async def list_available_schemas(request: Any) -> list[SchemaRegistryEntry] | ErrorResult:
            """List all available schemas in the EMQX Rule Engine

            Returns:
                result: a list of available schemas
            """

            result = await self.emqx_client.get("schema_registry")
            self.logger.info(f"Schema registry entries: {result}")

            return result

