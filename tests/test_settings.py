"""Tests for settings module."""

import json
import os
import tempfile
from pathlib import Path
import pytest

from dialog_gen.settings import (
    Settings, ModelSettings, GenerationSettings, StyleSettings,
    PromptSettings, ApiSettings, BrandDefaults, get_config_path
)


class TestModelSettings:
    """Tests for ModelSettings."""

    def test_defaults(self):
        """ModelSettings has correct defaults."""
        settings = ModelSettings()
        assert settings.default == "hermes3:8b"
        assert settings.fallback == "dolphin3:latest"
        assert len(settings.comparison) == 3

    def test_custom(self):
        """ModelSettings can be customized."""
        settings = ModelSettings(default="custom:latest")
        assert settings.default == "custom:latest"


class TestGenerationSettings:
    """Tests for GenerationSettings."""

    def test_defaults(self):
        """GenerationSettings has correct defaults."""
        settings = GenerationSettings()
        assert settings.temperature == 0.8
        assert settings.top_p == 0.9
        assert settings.max_tokens == 2048
        assert settings.default_turns == 4

    def test_validation(self):
        """GenerationSettings validates values."""
        with pytest.raises(ValueError):
            GenerationSettings(temperature=3.0)
        with pytest.raises(ValueError):
            GenerationSettings(top_p=1.5)


class TestStyleSettings:
    """Tests for StyleSettings."""

    def test_defaults(self):
        """StyleSettings has correct defaults."""
        settings = StyleSettings()
        assert settings.language == "ru"
        assert settings.max_message_length == 100
        assert settings.match_context_style is True
        assert settings.show_delays is True


class TestPromptSettings:
    """Tests for PromptSettings."""

    def test_has_ru_and_en(self):
        """PromptSettings has both language prompts."""
        settings = PromptSettings()
        assert settings.ru is not None
        assert settings.en is not None

    def test_ru_prompts(self):
        """Russian prompts are populated."""
        settings = PromptSettings()
        assert "телеграм" in settings.ru.system_prefix.lower()
        assert "НЕ ДЕЛАЙ" in settings.ru.negative_examples

    def test_en_prompts(self):
        """English prompts are populated."""
        settings = PromptSettings()
        assert "Telegram" in settings.en.system_prefix
        assert "WRITING RULES" in settings.en.style_rules


class TestCloudSettings:
    """Tests for CloudSettings."""

    def test_defaults(self):
        """CloudSettings has correct defaults."""
        from dialog_gen.settings import CloudSettings
        settings = CloudSettings()
        assert settings.provider == "ollama"
        assert settings.openai_api_key is None
        assert settings.anthropic_api_key is None
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.anthropic_model == "claude-3-haiku-20240307"

    def test_custom(self):
        """CloudSettings can be customized."""
        from dialog_gen.settings import CloudSettings
        settings = CloudSettings(
            provider="openai",
            openai_api_key="sk-test"
        )
        assert settings.provider == "openai"
        assert settings.openai_api_key == "sk-test"


class TestSettings:
    """Tests for main Settings class."""

    def test_defaults(self):
        """Settings initializes with defaults."""
        settings = Settings()
        assert settings.models is not None
        assert settings.generation is not None
        assert settings.style is not None
        assert settings.prompts is not None
        assert settings.cloud is not None
        assert settings.api is not None
        assert settings.brand_defaults is not None

    def test_backward_compat_properties(self):
        """Backward compatible properties work."""
        settings = Settings()
        assert settings.default_model == settings.models.default
        assert settings.temperature == settings.generation.temperature
        assert settings.top_p == settings.generation.top_p
        assert settings.max_tokens == settings.generation.max_tokens
        assert settings.ollama_base_url == settings.api.ollama_url

    def test_get_prompt(self):
        """get_prompt returns correct prompts."""
        settings = Settings()

        ru_prefix = settings.get_prompt("ru", "system_prefix")
        assert "телеграм" in ru_prefix.lower()

        en_prefix = settings.get_prompt("en", "system_prefix")
        assert "Telegram" in en_prefix

    def test_save_and_load(self):
        """Settings can be saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch config path
            import dialog_gen.settings as settings_module
            old_file = settings_module.CONFIG_FILE
            settings_module.CONFIG_FILE = Path(tmpdir) / "config.json"

            try:
                settings = Settings()
                settings.models.default = "test-model"
                settings.save()

                # Verify file exists
                assert settings_module.CONFIG_FILE.exists()

                # Load and verify
                loaded = Settings.load()
                assert loaded.models.default == "test-model"
            finally:
                settings_module.CONFIG_FILE = old_file

    def test_env_override(self):
        """Environment variables override config."""
        old_val = os.environ.get("DIALOG_GEN_MODEL")
        try:
            os.environ["DIALOG_GEN_MODEL"] = "env-model"
            settings = Settings.load()
            assert settings.models.default == "env-model"
        finally:
            if old_val:
                os.environ["DIALOG_GEN_MODEL"] = old_val
            else:
                os.environ.pop("DIALOG_GEN_MODEL", None)

    def test_model_dump(self):
        """Settings can be dumped to dict."""
        settings = Settings()
        data = settings.model_dump()

        assert "models" in data
        assert "generation" in data
        assert "style" in data
        assert "prompts" in data
        assert "api" in data
        assert "brand_defaults" in data

    def test_from_dict(self):
        """Settings can be created from dict."""
        data = {
            "models": {"default": "custom-model"},
            "generation": {"temperature": 0.5}
        }
        settings = Settings(**data)
        assert settings.models.default == "custom-model"
        assert settings.generation.temperature == 0.5
        # Defaults for unspecified
        assert settings.style.language == "ru"


class TestConfigPath:
    """Tests for config path."""

    def test_config_path(self):
        """Config path is in user home."""
        path = get_config_path()
        assert ".config" in str(path)
        assert "dialog-gen" in str(path)
        assert path.name == "config.json"
