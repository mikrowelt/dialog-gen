"""Tests for cloud client."""

import pytest
from dialog_gen.cloud_client import CloudClient


class TestCloudClient:
    """Tests for CloudClient class."""

    def test_init_defaults(self):
        """CloudClient initializes with defaults."""
        client = CloudClient()
        assert client.openrouter_api_key is None
        assert "openrouter.ai" in client.openrouter_base_url

    def test_init_with_key(self):
        """CloudClient accepts API key."""
        client = CloudClient(openrouter_api_key="sk-or-test")
        assert client.openrouter_api_key == "sk-or-test"


class TestListModels:
    """Tests for listing models."""

    @pytest.fixture
    def client(self):
        return CloudClient()

    @pytest.mark.asyncio
    async def test_list_models(self, client):
        """Lists known OpenRouter models."""
        models = await client.list_models()
        assert len(models) > 0
        assert any("claude" in m for m in models)


class TestGenerateErrors:
    """Tests for generation error handling."""

    @pytest.fixture
    def client(self):
        return CloudClient()

    @pytest.mark.asyncio
    async def test_no_key_error(self, client):
        """Raises error without OpenRouter key."""
        with pytest.raises(ValueError, match="OpenRouter API key not configured"):
            await client.generate(
                model="anthropic/claude-3-haiku-20240307",
                prompt="test",
            )
