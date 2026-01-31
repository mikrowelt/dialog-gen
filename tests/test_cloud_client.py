"""Tests for cloud client."""

import pytest
from dialog_gen.cloud_client import CloudClient


class TestCloudClient:
    """Tests for CloudClient class."""

    def test_init_defaults(self):
        """CloudClient initializes with defaults."""
        client = CloudClient()
        assert client.openai_api_key is None
        assert client.anthropic_api_key is None
        assert "openai.com" in client.openai_base_url
        assert "anthropic.com" in client.anthropic_base_url

    def test_init_with_keys(self):
        """CloudClient accepts API keys."""
        client = CloudClient(
            openai_api_key="sk-test",
            anthropic_api_key="sk-ant-test"
        )
        assert client.openai_api_key == "sk-test"
        assert client.anthropic_api_key == "sk-ant-test"


class TestDetectProvider:
    """Tests for provider detection."""

    @pytest.fixture
    def client(self):
        return CloudClient()

    def test_detect_openai_gpt(self, client):
        """Detects OpenAI from gpt- models."""
        assert client._detect_provider("gpt-4o-mini") == "openai"
        assert client._detect_provider("gpt-4") == "openai"
        assert client._detect_provider("GPT-4o") == "openai"

    def test_detect_openai_o1(self, client):
        """Detects OpenAI from o1- models."""
        assert client._detect_provider("o1-preview") == "openai"
        assert client._detect_provider("o1-mini") == "openai"

    def test_detect_anthropic_claude(self, client):
        """Detects Anthropic from claude models."""
        assert client._detect_provider("claude-3-haiku") == "anthropic"
        assert client._detect_provider("claude-sonnet-4") == "anthropic"
        assert client._detect_provider("claude-opus-4") == "anthropic"

    def test_detect_anthropic_shortnames(self, client):
        """Detects Anthropic from shortnames."""
        assert client._detect_provider("haiku") == "anthropic"
        assert client._detect_provider("sonnet") == "anthropic"
        assert client._detect_provider("opus") == "anthropic"

    def test_detect_ollama_default(self, client):
        """Defaults to ollama for unknown models."""
        assert client._detect_provider("hermes3:8b") == "ollama"
        assert client._detect_provider("dolphin3:latest") == "ollama"
        assert client._detect_provider("custom-model") == "ollama"


class TestListModels:
    """Tests for listing models."""

    @pytest.fixture
    def client(self):
        return CloudClient()

    @pytest.mark.asyncio
    async def test_list_anthropic_models(self, client):
        """Lists known Anthropic models."""
        models = await client.list_models("anthropic")
        assert len(models) > 0
        assert any("claude" in m for m in models)

    @pytest.mark.asyncio
    async def test_list_openai_no_key(self, client):
        """Returns empty list without API key."""
        models = await client.list_models("openai")
        assert models == []


class TestGenerateErrors:
    """Tests for generation error handling."""

    @pytest.fixture
    def client(self):
        return CloudClient()

    @pytest.mark.asyncio
    async def test_openai_no_key_error(self, client):
        """Raises error without OpenAI key."""
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            await client.generate(
                model="gpt-4o-mini",
                prompt="test",
                provider="openai"
            )

    @pytest.mark.asyncio
    async def test_anthropic_no_key_error(self, client):
        """Raises error without Anthropic key."""
        with pytest.raises(ValueError, match="Anthropic API key not configured"):
            await client.generate(
                model="claude-3-haiku",
                prompt="test",
                provider="anthropic"
            )

    @pytest.mark.asyncio
    async def test_unknown_provider_error(self, client):
        """Raises error for unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            await client.generate(
                model="test",
                prompt="test",
                provider="unknown"
            )
