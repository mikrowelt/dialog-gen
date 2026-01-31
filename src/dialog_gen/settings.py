"""
Unified configuration system for dialog-gen.

Configuration is loaded from (in order of priority):
1. Environment variables (DIALOG_GEN_* prefix)
2. Config file (~/.config/dialog-gen/config.json)
3. Default values

Usage:
    from dialog_gen.settings import settings

    # Access settings
    model = settings.models.default
    temp = settings.generation.temperature

    # Modify and save
    settings.models.default = "dolphin3:latest"
    settings.save()
"""

import json
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


# Config file location
CONFIG_DIR = Path.home() / ".config" / "dialog-gen"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ModelSettings(BaseModel):
    """Model selection settings."""
    default: str = Field(
        default="hermes3:8b",
        description="Default model for generation"
    )
    fallback: str = Field(
        default="dolphin3:latest",
        description="Fallback model if default unavailable"
    )
    comparison: list[str] = Field(
        default=["hermes3:8b", "dolphin3:latest", "nous-hermes2:10.7b"],
        description="Models for comparison tests"
    )


class GenerationSettings(BaseModel):
    """Generation parameters."""
    temperature: float = Field(default=0.8, ge=0, le=2, description="Creativity (0-2)")
    top_p: float = Field(default=0.9, ge=0, le=1, description="Nucleus sampling")
    max_tokens: int = Field(default=2048, ge=1, description="Max output tokens")
    default_turns: int = Field(default=4, ge=1, le=20, description="Default message count")


class StyleSettings(BaseModel):
    """Output style settings."""
    language: str = Field(default="ru", description="Default language: ru, en")
    max_message_length: int = Field(default=100, ge=10, description="Soft limit for message length")
    match_context_style: bool = Field(default=True, description="Match input message style")
    show_delays: bool = Field(default=True, description="Show typing delay hints in CLI")


class RuPromptSettings(BaseModel):
    """Russian language prompts."""
    system_prefix: str = Field(
        default="Ты продолжаешь реальный чат между людьми в телеграме.",
        description="System prompt prefix"
    )
    style_rules: str = Field(
        default="""СТИЛЬ - КРИТИЧЕСКИ ВАЖНО:
- Люди пишут ПО-ПРОСТОМУ, как в реальном чате, без пафоса и без литературного стиля
- Копируй ТОЧНО стиль входных сообщений: длину, пунктуацию, сокращения, эмодзи
- Реплики должны отличаться по стилю, чтобы не было ощущения что писал бот""",
        description="Style instructions"
    )
    negative_examples: str = Field(
        default="""НЕ ДЕЛАЙ ЭТО (негативные примеры):
- НЕ пиши "Хм, интересно", "Ого, круто!", "Звучит заманчиво" - это штампы
- НЕ используй сложные конструкции и длинные предложения
- НЕ пиши как реклама или продавец
- НЕ перегружай пунктуацией
- НЕ пиши длиннее чем сообщения в контексте""",
        description="What NOT to do"
    )
    brand_mention: str = Field(
        default="""КАК УПОМИНАТЬ БРЕНД:
- Мимоходом, между делом, как будто просто вспомнил
- Один человек упоминает, другой может спросить или не отреагировать
- Не расхваливай, просто факт""",
        description="How to mention brand naturally"
    )


class EnPromptSettings(BaseModel):
    """English language prompts."""
    system_prefix: str = Field(
        default="You write realistic Telegram chat between friends.",
        description="System prompt prefix"
    )
    style_rules: str = Field(
        default="""WRITING RULES:
- Write like real texting: lowercase, abbreviations (u, ur, rn, idk, lol, haha)
- Short messages, not paragraphs
- Reactions: "hmm", "oh", "nice", "wait", "hah"
- DON'T invent features not in description
- Responder reacts naturally - asks questions, shows interest, skepticism
- Conversation continues naturally after brand mention""",
        description="Style instructions"
    )


class PromptSettings(BaseModel):
    """All prompt templates."""
    ru: RuPromptSettings = Field(default_factory=RuPromptSettings)
    en: EnPromptSettings = Field(default_factory=EnPromptSettings)


class CloudSettings(BaseModel):
    """Cloud LLM provider settings."""
    provider: str = Field(
        default="openrouter",
        description="AI provider (openrouter)"
    )
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    openrouter_model: str = Field(
        default="anthropic/claude-3-haiku-20240307",
        description="Default OpenRouter model"
    )


class ApiSettings(BaseModel):
    """API server settings."""
    host: str = Field(default="0.0.0.0", description="API bind host")
    port: int = Field(default=8100, ge=1, le=65535, description="API port")


class BrandDefaults(BaseModel):
    """Default brand settings."""
    do_not_mention: list[str] = Field(
        default=["цены конкурентов", "недостатки"],
        description="Never mention these topics"
    )
    include_promo: bool = Field(default=False, description="Include promo codes by default")


class Settings(BaseModel):
    """Main settings container."""
    models: ModelSettings = Field(default_factory=ModelSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    style: StyleSettings = Field(default_factory=StyleSettings)
    prompts: PromptSettings = Field(default_factory=PromptSettings)
    cloud: CloudSettings = Field(default_factory=CloudSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    brand_defaults: BrandDefaults = Field(default_factory=BrandDefaults)

    # Computed properties for backward compatibility
    @property
    def default_model(self) -> str:
        """Backward compatible access to default model."""
        return self.models.default

    @property
    def temperature(self) -> float:
        """Backward compatible access to temperature."""
        return self.generation.temperature

    @property
    def top_p(self) -> float:
        """Backward compatible access to top_p."""
        return self.generation.top_p

    @property
    def max_tokens(self) -> int:
        """Backward compatible access to max_tokens."""
        return self.generation.max_tokens

    def save(self) -> None:
        """Save settings to config file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file and environment."""
        data = {}

        # Load from file if exists
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        # Override with environment variables
        env_mappings = {
            "DIALOG_GEN_MODEL": ("models", "default"),
            "DIALOG_GEN_TEMPERATURE": ("generation", "temperature"),
            "DIALOG_GEN_MAX_TOKENS": ("generation", "max_tokens"),
            "DIALOG_GEN_LANGUAGE": ("style", "language"),
            "DIALOG_GEN_API_HOST": ("api", "host"),
            "DIALOG_GEN_API_PORT": ("api", "port"),
            "DIALOG_GEN_PROVIDER": ("cloud", "provider"),
            "DIALOG_GEN_OPENROUTER_API_KEY": ("cloud", "openrouter_api_key"),
            "DIALOG_GEN_OPENROUTER_MODEL": ("cloud", "openrouter_model"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section not in data:
                    data[section] = {}
                # Type conversion
                if key in ("temperature", "top_p"):
                    value = float(value)
                elif key in ("max_tokens", "port", "default_turns"):
                    value = int(value)
                data[section][key] = value

        return cls(**data)

    def get_prompt(self, language: str, part: str) -> str:
        """Get prompt part for language.

        Args:
            language: 'ru' or 'en'
            part: 'system_prefix', 'style_rules', 'negative_examples', 'brand_mention'

        Returns:
            Prompt string
        """
        prompts = self.prompts.ru if language == "ru" else self.prompts.en
        return getattr(prompts, part, "")


def get_config_path() -> Path:
    """Get config file path."""
    return CONFIG_FILE


# Global settings instance
settings = Settings.load()


# Convenience functions for CLI
def load_config() -> Settings:
    """Reload settings from file."""
    global settings
    settings = Settings.load()
    return settings


def save_config(cfg: Settings) -> None:
    """Save settings to file."""
    global settings
    cfg.save()
    settings = cfg
