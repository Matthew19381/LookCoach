import pytest
from unittest import mock
from datetime import datetime
import httpx

from backend.services.integration_publisher import (
    IntegrationPublisher,
    ConfigurationError,
    PublishError,
    publish_protocol_done,
    publish_protocol_skipped,
    publish_state_observation,
    publish_aesthetic_priority_directive,
    publish_nutrition_needs_directive,
)


def mock_httpx_response(status_code: int, json_data: dict, text: str = ""):
    """Create a properly mocked httpx.Response."""
    response = mock.MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    response.text = text
    return response


class TestIntegrationPublisher:
    """Tests for IntegrationPublisher class."""
    
    @pytest.fixture
    def publisher(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-secret-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        return IntegrationPublisher()
    
    def test_init_with_env_vars(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "env-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://test:8000")
        pub = IntegrationPublisher()
        assert pub.module_key == "env-key"
        assert pub.hub_url == "http://test:8000"
        assert pub.endpoint == "http://test:8000/api/v1/integrations/event"
    
    def test_init_with_explicit_params(self):
        pub = IntegrationPublisher(
            hub_url="http://explicit:8000",
            module_key="explicit-key",
        )
        assert pub.module_key == "explicit-key"
        assert pub.hub_url == "http://explicit:8000"
    
    def test_init_missing_module_key_raises(self, monkeypatch):
        monkeypatch.delenv("MODULE_KEY", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            IntegrationPublisher()
        assert "MODULE_KEY not configured" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_event_type_raises(self, publisher):
        with pytest.raises(ValueError) as exc_info:
            await publisher.publish(
                event_type="invalid_type",
                user_id="user123",
                payload={},
            )
        assert "Invalid event_type" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_protocol_done_success(self, publisher):
        mock_response = mock_httpx_response(200, {"status": "received"})
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await publisher.publish(
                event_type="protocol_done",
                user_id="user123",
                payload={"protocol_id": "skincare_morning", "duration_seconds": 300, "completed_steps": ["cleanse", "vitamin_c", "spf"]},
            )
        
        assert result == {"status": "received"}
    
    @pytest.mark.asyncio
    async def test_publish_401_raises_configuration_error(self, publisher):
        mock_response = mock_httpx_response(401, {}, "Invalid X-Module-Key")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            with pytest.raises(ConfigurationError) as exc_info:
                await publisher.publish(
                    event_type="protocol_done",
                    user_id="user123",
                    payload={},
                )
        
        assert "Invalid X-Module-Key" in str(exc_info.value)
        assert "401" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_400_raises_publish_error(self, publisher):
        mock_response = mock_httpx_response(400, {}, "Bad Request")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            with pytest.raises(PublishError) as exc_info:
                await publisher.publish(
                    event_type="protocol_done",
                    user_id="user123",
                    payload={},
                )
        
        assert "400" in str(exc_info.value)
        assert "Bad Request" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_timeout_raises_publish_error(self, publisher):
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Timeout")
            with pytest.raises(PublishError) as exc_info:
                await publisher.publish(
                    event_type="protocol_done",
                    user_id="user123",
                    payload={},
                )
        
        assert "Timeout" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_network_error_raises_publish_error(self, publisher):
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")
            with pytest.raises(PublishError) as exc_info:
                await publisher.publish(
                    event_type="protocol_done",
                    user_id="user123",
                    payload={},
                )
        
        assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_publish_includes_correct_headers(self, publisher):
        captured = {}
        
        async def mock_post(self, url, json=None, headers=None, **kwargs):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return mock_httpx_response(200, {"status": "ok"})
        
        with mock.patch("httpx.AsyncClient.post", new=mock_post):
            await publisher.publish(
                event_type="protocol_skipped",
                user_id="user456",
                payload={"protocol_id": "test", "reason": "no_time"},
            )
        
        assert captured["url"] == "http://localhost:8000/api/v1/integrations/event"
        assert captured["headers"]["X-Module-Key"] == "test-secret-key"
        assert captured["headers"]["Content-Type"] == "application/json"
        assert captured["json"]["source_module"] == "lookcoach"
        assert captured["json"]["event_type"] == "protocol_skipped"
        assert captured["json"]["user_id"] == "user456"
        assert "timestamp" in captured["json"]
        assert captured["json"]["payload"] == {"protocol_id": "test", "reason": "no_time"}


class TestConvenienceFunctions:
    """Tests for convenience publish functions."""
    
    @pytest.mark.asyncio
    async def test_publish_protocol_done(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_protocol_done(
                user_id="user1",
                protocol_id="skincare_evening",
                duration_seconds=600,
                completed_steps=["cleanse", "retinol", "moisturize"],
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_protocol_skipped(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_protocol_skipped(
                user_id="user2",
                protocol_id="skincare_morning",
                reason="overslept",
                skipped_at_step="vitamin_c",
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_state_observation(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_state_observation(
                user_id="user3",
                observation_type="skin_hydration",
                data={"level": "low", "area": "cheeks"},
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_protocol_skipped_without_optional_skipped_at_step(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_protocol_skipped(
                user_id="user2",
                protocol_id="skincare_morning",
                reason="forgot",
            )
        
        assert result == {"status": "ok"}


class TestEventTypes:
    """Test that all three required event types work."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("event_type", ["protocol_done", "protocol_skipped", "state_observation"])
    async def test_all_three_event_types(self, event_type, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            publisher = IntegrationPublisher()
            result = await publisher.publish(
                event_type=event_type,
                user_id="user_test",
                payload={"test": "data"},
            )
        
        assert result == {"status": "ok"}


class TestNewEventTypes:
    """Test the new event types for INT-3."""
    
    @pytest.mark.asyncio
    async def test_aesthetic_priority_directive_valid(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            publisher = IntegrationPublisher()
            result = await publisher.publish(
                event_type="aesthetic_priority_directive",
                user_id="user123",
                payload={
                    "priority_area": "V-taper",
                    "priority_level": "high",
                    "reason": "Wide shoulders needed for aesthetic balance",
                    "target_module": "ForgeBody",
                },
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_nutrition_needs_directive_valid(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            publisher = IntegrationPublisher()
            result = await publisher.publish(
                event_type="nutrition_needs_directive",
                user_id="user123",
                payload={
                    "sodium_limit_mg": 1500,
                    "dairy_restriction": True,
                    "reason": "Reduce facial puffiness before event",
                    "target_module": "Dieta",
                },
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_nutrition_needs_directive_partial_payload(self, monkeypatch):
        """Test nutrition directive with only sodium limit."""
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            publisher = IntegrationPublisher()
            result = await publisher.publish(
                event_type="nutrition_needs_directive",
                user_id="user123",
                payload={
                    "sodium_limit_mg": 1000,
                    "reason": "Pre-event protocol",
                    "target_module": "Dieta",
                },
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_aesthetic_priority_directive_invalid_priority_level(self, monkeypatch):
        """Test that invalid priority levels are rejected by the hub (not locally validated)."""
        # The publisher doesn't validate priority_level locally - that's a hub concern
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            publisher = IntegrationPublisher()
            result = await publisher.publish(
                event_type="aesthetic_priority_directive",
                user_id="user123",
                payload={
                    "priority_area": "V-taper",
                    "priority_level": "invalid",  # Not validated locally
                    "reason": "Test",
                    "target_module": "ForgeBody",
                },
            )
        
        assert result == {"status": "ok"}


class TestConvenienceFunctionsNew:
    """Tests for new convenience publish functions."""
    
    @pytest.mark.asyncio
    async def test_publish_aesthetic_priority_directive(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_aesthetic_priority_directive(
                user_id="user1",
                priority_area="shoulders",
                priority_level="high",
                reason="Missing delts for V-taper",
                target_module="ForgeBody",
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_nutrition_needs_directive_full(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_nutrition_needs_directive(
                user_id="user2",
                sodium_mg=1500,
                dairy_restriction=True,
                reason="Pre-event puffiness reduction",
                target_module="Dieta",
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_nutrition_needs_directive_sodium_only(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_nutrition_needs_directive(
                user_id="user3",
                sodium_mg=1000,
                reason="Reduce water retention",
            )
        
        assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_publish_nutrition_needs_directive_dairy_only(self, monkeypatch):
        monkeypatch.setenv("MODULE_KEY", "test-key")
        monkeypatch.setenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000")
        
        with mock.patch("httpx.AsyncClient.post", new_callable=mock.AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response(200, {"status": "ok"})
            result = await publish_nutrition_needs_directive(
                user_id="user4",
                dairy_restriction=False,
                reason="No dairy issue",
            )
        
        assert result == {"status": "ok"}