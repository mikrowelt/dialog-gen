"""Tests for shared utilities."""

import pytest
from dialog_gen.utils import detect_provider


class TestDetectProvider:
    """Tests for detect_provider function."""

    def test_detect_openai_gpt_models(self):
        """Detects OpenAI from gpt- prefixed models."""
        assert detect_provider("gpt-4o-mini") == "openai"
        assert detect_provider("gpt-4") == "openai"
        assert detect_provider("gpt-4o") == "openai"
        assert detect_provider("gpt-3.5-turbo") == "openai"

    def test_detect_openai_case_insensitive(self):
        """Detection is case insensitive."""
        assert detect_provider("GPT-4o") == "openai"
        assert detect_provider("GPT-4O-MINI") == "openai"

    def test_detect_openai_o1_models(self):
        """Detects OpenAI from o1- prefixed models."""
        assert detect_provider("o1-preview") == "openai"
        assert detect_provider("o1-mini") == "openai"

    def test_detect_openai_legacy_models(self):
        """Detects OpenAI from legacy model names."""
        assert detect_provider("davinci") == "openai"
        assert detect_provider("text-davinci-003") == "openai"
        assert detect_provider("chatgpt-4o") == "openai"

    def test_detect_anthropic_claude_models(self):
        """Detects Anthropic from claude models."""
        assert detect_provider("claude-3-haiku-20240307") == "anthropic"
        assert detect_provider("claude-3-5-sonnet-20241022") == "anthropic"
        assert detect_provider("claude-sonnet-4-20250514") == "anthropic"
        assert detect_provider("claude-opus-4-20250514") == "anthropic"

    def test_detect_anthropic_shortnames(self):
        """Detects Anthropic from shorthand names."""
        assert detect_provider("haiku") == "anthropic"
        assert detect_provider("sonnet") == "anthropic"
        assert detect_provider("opus") == "anthropic"
        assert detect_provider("HAIKU") == "anthropic"

    def test_detect_ollama_default(self):
        """Defaults to ollama for unknown models."""
        assert detect_provider("hermes3:8b") == "ollama"
        assert detect_provider("dolphin3:latest") == "ollama"
        assert detect_provider("llama3.1:8b") == "ollama"
        assert detect_provider("custom-model") == "ollama"
        assert detect_provider("local-model:v1") == "ollama"

    def test_detect_with_tags_and_versions(self):
        """Handles models with tags and version suffixes."""
        assert detect_provider("gpt-4o-mini:latest") == "openai"
        assert detect_provider("claude-3-haiku:v1") == "anthropic"
        assert detect_provider("mistral:7b") == "ollama"
