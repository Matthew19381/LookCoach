import os
import httpx
import json
from typing import Optional
from datetime import datetime


class IntegrationPublisher:
    """
    Outgoing publisher for LookCoach events to System-Główny hub.
    
    Events: protocol_done, protocol_skipped, state_observation,
            aesthetic_priority_directive, nutrition_needs_directive
    Endpoint: :8000/api/v1/integrations/event
    Auth: X-Module-Key header
    
    401 is treated as configuration error, not silent failure.
    """
    
    def __init__(
        self,
        hub_url: str = None,
        module_key: str = None,
        timeout: float = 10.0,
    ):
        self.hub_url = hub_url or os.getenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        self.module_key = module_key or os.getenv("MODULE_KEY")
        self.timeout = timeout
        self.endpoint = f"{self.hub_url.rstrip('/')}/api/v1/integrations/event"
        
        if not self.module_key:
            raise ConfigurationError(
                "MODULE_KEY not configured. Set MODULE_KEY in environment "
                "or pass module_key to IntegrationPublisher."
            )
    
    async def publish(
        self,
        event_type: str,
        user_id: str,
        payload: dict,
        timestamp: Optional[str] = None,
    ) -> dict:
        """
        Publish an event to System-Główny hub.
        
        Args:
            event_type: One of 'protocol_done', 'protocol_skipped', 'state_observation',
                        'aesthetic_priority_directive', 'nutrition_needs_directive'
            user_id: User identifier
            payload: Event-specific payload
            timestamp: ISO format timestamp (defaults to now)
           
        Returns:
            Response from hub
           
        Raises:
            ConfigurationError: If MODULE_KEY is invalid (401 from hub)
            PublishError: On network/timeout errors
        """
        valid_event_types = (
            "protocol_done", 
            "protocol_skipped", 
            "state_observation",
            "aesthetic_priority_directive",
            "nutrition_needs_directive",
        )
        if event_type not in valid_event_types:
            raise ValueError(
                f"Invalid event_type: {event_type}. "
                f"Must be one of: {', '.join(valid_event_types)}"
            )
        
        event = {
            "source_module": "lookcoach",
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
            "payload": payload,
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Module-Key": self.module_key,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.endpoint,
                    json=event,
                    headers=headers,
                )
            except httpx.TimeoutException as e:
                raise PublishError(f"Timeout publishing to hub: {e}") from e
            except httpx.RequestError as e:
                raise PublishError(f"Network error publishing to hub: {e}") from e
            
            if response.status_code == 401:
                raise ConfigurationError(
                    "Invalid X-Module-Key (401 from hub). Check MODULE_KEY configuration. "
                    f"Hub response: {response.text}"
                )
            elif response.status_code >= 400:
                raise PublishError(
                    f"Hub returned {response.status_code}: {response.text}"
                )
            
            return response.json()


class ConfigurationError(Exception):
    """Raised when publisher configuration is invalid (e.g., bad MODULE_KEY)."""
    pass


class PublishError(Exception):
    """Raised when publishing fails due to network or hub errors."""
    pass


# Convenience functions for common event types

async def publish_protocol_done(
    user_id: str,
    protocol_id: str,
    duration_seconds: int,
    completed_steps: list[str],
    hub_url: str = None,
    module_key: str = None,
) -> dict:
    """Publish protocol_done event."""
    publisher = IntegrationPublisher(hub_url=hub_url, module_key=module_key)
    return await publisher.publish(
        event_type="protocol_done",
        user_id=user_id,
        payload={
            "protocol_id": protocol_id,
            "duration_seconds": duration_seconds,
            "completed_steps": completed_steps,
        },
    )


async def publish_protocol_skipped(
    user_id: str,
    protocol_id: str,
    reason: str,
    skipped_at_step: Optional[str] = None,
    hub_url: str = None,
    module_key: str = None,
) -> dict:
    """Publish protocol_skipped event."""
    publisher = IntegrationPublisher(hub_url=hub_url, module_key=module_key)
    return await publisher.publish(
        event_type="protocol_skipped",
        user_id=user_id,
        payload={
            "protocol_id": protocol_id,
            "reason": reason,
            "skipped_at_step": skipped_at_step,
        },
    )


async def publish_state_observation(
    user_id: str,
    observation_type: str,
    data: dict,
    hub_url: str = None,
    module_key: str = None,
) -> dict:
    """Publish state_observation event."""
    publisher = IntegrationPublisher(hub_url=hub_url, module_key=module_key)
    return await publisher.publish(
        event_type="state_observation",
        user_id=user_id,
        payload={
            "observation_type": observation_type,
            "data": data,
        },
    )


async def publish_aesthetic_priority_directive(
    user_id: str,
    priority_area: str,
    priority_level: str,
    reason: str,
    target_module: str = "ForgeBody",
    hub_url: str = None,
    module_key: str = None,
) -> dict:
    """
    Publish aesthetic_priority_directive event.
    
    Args:
        user_id: User identifier
        priority_area: The aesthetic area needing priority (e.g., "V-taper", "shoulders", "posture")
        priority_level: "high" | "medium" | "low"
        reason: Why this is a priority (from AI analysis)
        target_module: Target module to receive directive (default: "ForgeBody")
        hub_url: Optional hub URL override
        module_key: Optional module key override
    """
    publisher = IntegrationPublisher(hub_url=hub_url, module_key=module_key)
    return await publisher.publish(
        event_type="aesthetic_priority_directive",
        user_id=user_id,
        payload={
            "priority_area": priority_area,
            "priority_level": priority_level,
            "reason": reason,
            "target_module": target_module,
        },
    )


async def publish_nutrition_needs_directive(
    user_id: str,
    sodium_mg: Optional[int] = None,
    dairy_restriction: Optional[bool] = None,
    reason: str = "",
    target_module: str = "Dieta",
    hub_url: str = None,
    module_key: str = None,
) -> dict:
    """
    Publish nutrition_needs_directive event.
    
    Args:
        user_id: User identifier
        sodium_mg: Recommended sodium limit in mg (e.g., 1500 for puffiness reduction)
        dairy_restriction: Whether to restrict dairy (for puffiness/bloating)
        reason: Why this directive is needed (from AI analysis)
        target_module: Target module to receive directive (default: "Dieta")
        hub_url: Optional hub URL override
        module_key: Optional module key override
    """
    publisher = IntegrationPublisher(hub_url=hub_url, module_key=module_key)
    payload = {"target_module": target_module, "reason": reason}
    if sodium_mg is not None:
        payload["sodium_limit_mg"] = sodium_mg
    if dairy_restriction is not None:
        payload["dairy_restriction"] = dairy_restriction
    return await publisher.publish(
        event_type="nutrition_needs_directive",
        user_id=user_id,
        payload=payload,
    )