"""
Pydantic models for dialog generation.

This module defines all the data models used throughout the application
for representing subjects (brands, topics, info), campaigns, dialogs,
and API requests/responses.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator


# Valid subject types
SubjectType = Literal["brand", "product", "service", "topic", "info", "event"]
VALID_SUBJECT_TYPES = {"brand", "product", "service", "topic", "info", "event"}

# Valid mention styles
MentionStyle = Literal["natural", "casual", "enthusiastic", "skeptical"]
VALID_MENTION_STYLES = {"natural", "casual", "enthusiastic", "skeptical"}

# Subject type labels for prompts (multi-language support)
SUBJECT_TYPE_LABELS = {
    "ru": {
        "brand": "БРЕНД",
        "product": "ПРОДУКТ",
        "service": "СЕРВИС",
        "topic": "ТЕМА",
        "info": "ИНФОРМАЦИЯ",
        "event": "СОБЫТИЕ",
        "default": "ПРЕДМЕТ"
    },
    "en": {
        "brand": "BRAND",
        "product": "PRODUCT",
        "service": "SERVICE",
        "topic": "TOPIC",
        "info": "INFO",
        "event": "EVENT",
        "default": "SUBJECT"
    }
}

# Mention instruction templates (multi-language)
MENTION_INSTRUCTIONS = {
    "ru": {
        "brand": "Упомяни {name} мимоходом, как личный опыт",
        "product": "Упомяни {name} естественно, как покупку или рекомендацию",
        "service": "Упомяни {name} мимоходом, как личный опыт использования",
        "topic": "Затроньте тему {name} естественно в разговоре",
        "info": "Включи информацию о {name} в диалог",
        "event": "Упомяни событие {name} в контексте разговора",
        "default": "Упомяни {name} естественно в разговоре"
    },
    "en": {
        "brand": "Mention {name} casually, as personal experience",
        "product": "Mention {name} naturally, as a purchase or recommendation",
        "service": "Mention {name} casually, as a personal experience",
        "topic": "Touch on the topic of {name} naturally in conversation",
        "info": "Include information about {name} in the dialog",
        "event": "Mention the event {name} in conversation context",
        "default": "Mention {name} naturally in conversation"
    }
}


class Subject(BaseModel):
    """Generic subject for dialog injection.

    Represents any subject that should be naturally mentioned
    in the generated dialog - can be a brand, topic, info, etc.

    Attributes:
        name: Subject name (e.g., "FoodBox", "Bitcoin ETF", "Python 3.13").
        description: What it is (e.g., "food delivery service", "new features").
        type: Subject type (brand, product, service, topic, info, event).
        attributes: Key points/features to potentially mention.
        constraints: What NOT to mention.
        mention_style: How to mention (natural, casual, enthusiastic, skeptical).
        context_hint: Extra context for LLM.
        promo: Optional promotional info {code: "X", benefit: "Y"}.

    Example:
        >>> # Brand/product marketing
        >>> subject = Subject(
        ...     name="FoodBox",
        ...     description="food delivery service",
        ...     type="brand",
        ...     attributes=["fast delivery", "many restaurants"]
        ... )

        >>> # Topic injection
        >>> subject = Subject(
        ...     name="Bitcoin ETF",
        ...     description="investment news",
        ...     type="topic"
        ... )

        >>> # Information seeding
        >>> subject = Subject(
        ...     name="Python 3.13",
        ...     description="new features",
        ...     type="info",
        ...     attributes=["GIL removal", "JIT compiler"]
        ... )
    """
    name: str = Field(description="Subject name, e.g. 'FoodBox', 'Bitcoin ETF'")
    description: str = Field(description="What it is, e.g. 'food delivery', 'investment news'")
    type: str = Field(
        default="brand",
        description="Type: brand, product, service, topic, info, event"
    )
    attributes: list[str] = Field(
        default_factory=list,
        description="Key points/features to mention"
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="What NOT to mention"
    )
    mention_style: str = Field(
        default="natural",
        description="How to mention: natural, casual, enthusiastic, skeptical"
    )
    context_hint: Optional[str] = Field(
        default=None,
        description="Extra context for LLM"
    )
    promo: Optional[dict] = Field(
        default=None,
        description="Promo info: {code: 'X', benefit: 'Y'}"
    )

    # Backward compatibility aliases
    @property
    def what_is_it(self) -> str:
        """Alias for description (backward compat with Brand)."""
        return self.description

    @property
    def features(self) -> list[str]:
        """Alias for attributes (backward compat with Brand)."""
        return self.attributes

    @property
    def do_not_mention(self) -> list[str]:
        """Alias for constraints (backward compat with Brand)."""
        return self.constraints

    @property
    def promo_code(self) -> Optional[str]:
        """Alias for promo.code (backward compat with Brand)."""
        return self.promo.get("code") if self.promo else None

    @property
    def promo_benefit(self) -> Optional[str]:
        """Alias for promo.benefit (backward compat with Brand)."""
        return self.promo.get("benefit") if self.promo else None

    @property
    def topic(self) -> Optional[str]:
        """Alias for context_hint (backward compat with Brand)."""
        return self.context_hint

    def get_type_label(self, language: str = "ru") -> str:
        """Get localized label for subject type."""
        labels = SUBJECT_TYPE_LABELS.get(language, SUBJECT_TYPE_LABELS["en"])
        return labels.get(self.type, labels["default"])

    def get_mention_instruction(self, language: str = "ru") -> str:
        """Get localized mention instruction for subject type."""
        instructions = MENTION_INSTRUCTIONS.get(language, MENTION_INSTRUCTIONS["en"])
        template = instructions.get(self.type, instructions["default"])
        return template.format(name=self.name)


def Brand(
    name: str,
    what_is_it: Optional[str] = None,
    description: Optional[str] = None,
    topic: Optional[str] = None,
    features: Optional[list[str]] = None,
    attributes: Optional[list[str]] = None,
    promo_code: Optional[str] = None,
    promo_benefit: Optional[str] = None,
    promo: Optional[dict] = None,
    do_not_mention: Optional[list[str]] = None,
    constraints: Optional[list[str]] = None,
    mention_style: str = "natural",
    context_hint: Optional[str] = None,
    **kwargs
) -> Subject:
    """Create a Brand (Subject with type='brand') for backward compatibility.

    This factory function accepts both legacy Brand field names and new Subject
    field names, making migration seamless.

    Args:
        name: Brand name (e.g., "FoodBox").
        what_is_it: What the brand is (legacy, maps to description).
        description: What it is (new style).
        topic: Topic category (legacy, maps to context_hint).
        features: Key features (legacy, maps to attributes).
        attributes: Key points (new style).
        promo_code: Promotional code (legacy).
        promo_benefit: What the promo gives (legacy).
        promo: Promo info dict (new style).
        do_not_mention: Topics to avoid (legacy, maps to constraints).
        constraints: What NOT to mention (new style).
        mention_style: How to mention (natural, casual, etc.).
        context_hint: Extra context for LLM.

    Example:
        >>> # Legacy style
        >>> brand = Brand(
        ...     name="FoodBox",
        ...     what_is_it="food delivery service",
        ...     features=["fast delivery", "many restaurants"]
        ... )

        >>> # New style (also works)
        >>> brand = Brand(
        ...     name="FoodBox",
        ...     description="food delivery service",
        ...     attributes=["fast delivery", "many restaurants"]
        ... )

    Returns:
        Subject instance with type="brand".
    """
    # Map legacy fields to new fields
    actual_description = description or what_is_it or ""
    actual_attributes = attributes or features or []
    actual_constraints = constraints or do_not_mention or []
    actual_context_hint = context_hint or topic

    # Build promo dict from legacy fields if needed
    actual_promo = promo
    if actual_promo is None and (promo_code or promo_benefit):
        actual_promo = {}
        if promo_code:
            actual_promo["code"] = promo_code
        if promo_benefit:
            actual_promo["benefit"] = promo_benefit

    return Subject(
        name=name,
        description=actual_description,
        type="brand",
        attributes=actual_attributes,
        constraints=actual_constraints,
        mention_style=mention_style,
        context_hint=actual_context_hint,
        promo=actual_promo
    )


class Campaign(BaseModel):
    """Campaign settings for dialog generation.

    Controls the tone, style, and goals of the generated dialog.

    Attributes:
        goal: Campaign objective (awareness, engagement, information, trial, conversion).
        style: Dialog style (casual, enthusiastic, skeptical, curious).
        mention_type: How to mention subject (natural, recommendation, personal_experience, question).
        include_promo: Whether to include promotional codes.
        urgency: Whether to add urgency messaging.

    Example:
        >>> campaign = Campaign(
        ...     goal="awareness",
        ...     style="casual",
        ...     mention_type="personal_experience"
        ... )
    """
    goal: str = Field(
        default="awareness",
        description="Campaign goal: awareness, engagement, information, trial, conversion"
    )
    style: str = Field(
        default="casual",
        description="Dialog style: casual, enthusiastic, skeptical, curious"
    )
    mention_type: str = Field(
        default="natural",
        description="How to mention: natural, recommendation, personal_experience, question"
    )
    include_promo: bool = Field(default=False, description="Include promo codes")
    urgency: bool = Field(default=False, description="Add urgency like 'limited time'")

    # Backward compatibility
    brand_mention_type: Optional[str] = Field(default=None, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data):
        """Map legacy Campaign fields."""
        if isinstance(data, dict):
            # Map brand_mention_type -> mention_type
            if "brand_mention_type" in data and not data.get("mention_type"):
                data["mention_type"] = data["brand_mention_type"]
        return data


class DialogContext(BaseModel):
    """Conversation context for continuation.

    Provides previous messages and metadata for context-aware generation.

    Attributes:
        messages: Previous messages with role and content.
        topic: Optional conversation topic.
        setting: Optional setting description.

    Example:
        >>> context = DialogContext(
        ...     messages=[
        ...         {"role": "person1", "content": "hi"},
        ...         {"role": "person2", "content": "hey!"}
        ...     ],
        ...     topic="casual chat"
        ... )
    """
    messages: list[dict[str, str]] = Field(
        default_factory=list,
        description="Previous messages [{role: 'person1', content: '...'}]"
    )
    topic: Optional[str] = Field(default=None, description="Conversation topic")
    setting: Optional[str] = Field(default=None, description="Setting description")


class DialogMessage(BaseModel):
    """A single message in a dialog.

    Represents one turn in the conversation.

    Attributes:
        role: Speaker identifier (person1, person2, person3, etc.).
        content: Message text.
        delay_hint: Suggested typing delay in seconds.

    Example:
        >>> msg = DialogMessage(
        ...     role="person1",
        ...     content="Have you tried FoodBox?",
        ...     delay_hint=2.5
        ... )
    """
    role: str = Field(description="Speaker: person1, person2, person3, etc.")
    content: str = Field(description="Message text")
    delay_hint: Optional[float] = Field(
        default=None,
        description="Suggested delay before sending (seconds)"
    )


class GeneratedDialog(BaseModel):
    """Generated dialog output.

    Contains the generated messages and metadata about the generation.

    Attributes:
        messages: List of generated messages.
        model_used: Name of the model that generated the dialog.
        generation_params: Parameters and metrics from generation.

    Example:
        >>> dialog = GeneratedDialog(
        ...     messages=[DialogMessage(role="person1", content="hi")],
        ...     model_used="hermes3:8b",
        ...     generation_params={"temperature": 0.8, "generation_time_ms": 1500}
        ... )
    """
    messages: list[DialogMessage] = Field(description="Generated messages")
    model_used: str = Field(description="Model that generated the dialog")
    generation_params: dict = Field(description="Generation parameters and metrics")


class _SubjectRequestMixin:
    """Mixin providing subject/brand handling for request models."""

    @model_validator(mode="before")
    @classmethod
    def handle_brand_alias(cls, data):
        """Handle brand as alias for subject."""
        if isinstance(data, dict):
            if data.get("brand") and not data.get("subject"):
                data["subject"] = data["brand"]
        return data

    @model_validator(mode="after")
    def require_subject(self):
        """Ensure subject is provided (via subject or brand)."""
        if self.subject is None:
            raise ValueError("Either 'subject' or 'brand' must be provided")
        return self


class GenerateRequest(_SubjectRequestMixin, BaseModel):
    """Request to generate a dialog.

    Contains all parameters needed for dialog generation.

    Attributes:
        subject: Subject information to mention (brand, topic, info, etc.).
        brand: Alias for subject (backward compatibility).
        campaign: Campaign settings for tone and style.
        context: Optional conversation context to continue.
        num_turns: Number of messages to generate.
        model: Optional model override.
        temperature: Optional temperature override.
        language: Language code (ru, en).

    Example:
        >>> # New flexible way
        >>> request = GenerateRequest(
        ...     subject=Subject(name="Bitcoin ETF", description="investment news", type="topic"),
        ...     num_turns=4
        ... )

        >>> # Old way still works
        >>> request = GenerateRequest(
        ...     brand=Brand(name="FoodBox", what_is_it="food delivery"),
        ...     num_turns=4
        ... )
    """
    subject: Optional[Subject] = Field(default=None, description="Subject to mention")
    brand: Optional[Subject] = Field(default=None, description="Brand (alias for subject)", exclude=True)
    campaign: Campaign = Field(default_factory=Campaign, description="Campaign settings")
    context: Optional[DialogContext] = Field(default=None, description="Conversation context")
    num_turns: int = Field(default=4, ge=1, le=20, description="Number of messages")
    model: Optional[str] = Field(default=None, description="Model override")
    temperature: Optional[float] = Field(default=None, ge=0, le=2, description="Temperature")
    language: str = Field(default="ru", description="Language: en, ru")


class SingleResponseRequest(_SubjectRequestMixin, BaseModel):
    """Request to generate a single response.

    Used for continuing a conversation one message at a time.

    Attributes:
        subject: Subject information.
        brand: Alias for subject (backward compatibility).
        campaign: Campaign settings.
        context: Required conversation context.
        model: Optional model override.
        temperature: Optional temperature override.
        language: Language code.
    """
    subject: Optional[Subject] = Field(default=None, description="Subject to mention")
    brand: Optional[Subject] = Field(default=None, description="Brand (alias for subject)", exclude=True)
    campaign: Campaign = Field(default_factory=Campaign, description="Campaign settings")
    context: DialogContext = Field(description="Conversation context (required)")
    model: Optional[str] = Field(default=None, description="Model override")
    temperature: Optional[float] = Field(default=None, description="Temperature")
    language: str = Field(default="ru", description="Language: en, ru")


class ModelInfo(BaseModel):
    """Information about an available model.

    Represents metadata about an available model.

    Attributes:
        name: Model name/tag.
        size: Human-readable size.
        modified_at: Last modification timestamp.
        digest: Short model digest hash.
    """
    name: str = Field(description="Model name/tag")
    size: Optional[str] = Field(default=None, description="Human-readable size")
    modified_at: Optional[str] = Field(default=None, description="Last modified")
    digest: Optional[str] = Field(default=None, description="Model digest")


class CompareRequest(_SubjectRequestMixin, BaseModel):
    """Request to compare multiple models.

    Used for running the same generation across different models.

    Attributes:
        subject: Subject information.
        brand: Alias for subject (backward compatibility).
        campaign: Campaign settings.
        context: Optional conversation context.
        models: List of model names to compare.
        num_turns: Number of messages per model.
        language: Language code.
    """
    subject: Optional[Subject] = Field(default=None, description="Subject to mention")
    brand: Optional[Subject] = Field(default=None, description="Brand (alias for subject)", exclude=True)
    campaign: Campaign = Field(default_factory=Campaign, description="Campaign settings")
    context: Optional[DialogContext] = Field(default=None, description="Context")
    models: list[str] = Field(description="Models to compare")
    num_turns: int = Field(default=4, description="Messages per model")
    language: str = Field(default="ru", description="Language: en, ru")


class CompareResult(BaseModel):
    """Result from model comparison.

    Contains the generated dialog and timing for one model.

    Attributes:
        model: Model name that was used.
        dialog: Generated dialog output.
        generation_time_ms: Time taken in milliseconds.
    """
    model: str = Field(description="Model name")
    dialog: GeneratedDialog = Field(description="Generated dialog")
    generation_time_ms: int = Field(description="Generation time in ms")
