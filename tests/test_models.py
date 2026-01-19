"""Tests for Pydantic models."""

import pytest
from dialog_gen.models import (
    Subject, Brand, Campaign, DialogContext, DialogMessage,
    GeneratedDialog, GenerateRequest, SingleResponseRequest,
    ModelInfo, CompareRequest, CompareResult
)


class TestSubject:
    """Tests for Subject model."""

    def test_minimal_subject(self):
        """Subject can be created with just name and description."""
        subject = Subject(name="TestSubject", description="test description")
        assert subject.name == "TestSubject"
        assert subject.description == "test description"
        assert subject.type == "brand"  # default
        assert subject.attributes == []
        assert subject.constraints == []
        assert subject.mention_style == "natural"

    def test_full_subject(self):
        """Subject can be created with all fields."""
        subject = Subject(
            name="Bitcoin ETF",
            description="investment news",
            type="topic",
            attributes=["SEC approved", "major milestone"],
            constraints=["specific tickers"],
            mention_style="casual",
            context_hint="financial markets",
            promo={"code": "INVEST10", "benefit": "10% off"}
        )
        assert subject.name == "Bitcoin ETF"
        assert subject.description == "investment news"
        assert subject.type == "topic"
        assert len(subject.attributes) == 2
        assert subject.promo_code == "INVEST10"
        assert subject.promo_benefit == "10% off"

    def test_subject_type_label_ru(self):
        """Subject returns correct Russian type label."""
        brand = Subject(name="Test", description="test", type="brand")
        topic = Subject(name="Test", description="test", type="topic")
        info = Subject(name="Test", description="test", type="info")

        assert brand.get_type_label("ru") == "БРЕНД"
        assert topic.get_type_label("ru") == "ТЕМА"
        assert info.get_type_label("ru") == "ИНФОРМАЦИЯ"

    def test_subject_type_label_en(self):
        """Subject returns correct English type label."""
        brand = Subject(name="Test", description="test", type="brand")
        topic = Subject(name="Test", description="test", type="topic")
        info = Subject(name="Test", description="test", type="info")

        assert brand.get_type_label("en") == "BRAND"
        assert topic.get_type_label("en") == "TOPIC"
        assert info.get_type_label("en") == "INFO"

    def test_subject_mention_instruction_ru(self):
        """Subject returns correct Russian mention instruction."""
        brand = Subject(name="FoodBox", description="test", type="brand")
        topic = Subject(name="Bitcoin", description="test", type="topic")

        assert "FoodBox" in brand.get_mention_instruction("ru")
        assert "мимоходом" in brand.get_mention_instruction("ru")
        assert "Bitcoin" in topic.get_mention_instruction("ru")
        assert "тему" in topic.get_mention_instruction("ru")

    def test_subject_mention_instruction_en(self):
        """Subject returns correct English mention instruction."""
        brand = Subject(name="FoodBox", description="test", type="brand")
        topic = Subject(name="Bitcoin", description="test", type="topic")

        assert "FoodBox" in brand.get_mention_instruction("en")
        assert "casually" in brand.get_mention_instruction("en")
        assert "Bitcoin" in topic.get_mention_instruction("en")
        assert "topic" in topic.get_mention_instruction("en")

    def test_subject_backward_compat_properties(self):
        """Subject provides backward compatibility properties."""
        subject = Subject(
            name="Test",
            description="test desc",
            attributes=["feat1", "feat2"],
            constraints=["avoid1"],
            context_hint="some context",
            promo={"code": "ABC", "benefit": "discount"}
        )

        # These properties should work for backward compatibility with Brand
        assert subject.what_is_it == "test desc"
        assert subject.features == ["feat1", "feat2"]
        assert subject.do_not_mention == ["avoid1"]
        assert subject.topic == "some context"
        assert subject.promo_code == "ABC"
        assert subject.promo_benefit == "discount"


class TestBrand:
    """Tests for Brand factory function (backward compatibility)."""

    def test_minimal_brand(self):
        """Brand can be created with just name and what_is_it."""
        brand = Brand(name="TestBrand", what_is_it="test service")
        assert brand.name == "TestBrand"
        assert brand.description == "test service"  # mapped from what_is_it
        assert brand.what_is_it == "test service"  # backward compat property
        assert brand.attributes == []
        assert brand.type == "brand"

    def test_full_brand(self):
        """Brand can be created with all legacy fields."""
        brand = Brand(
            name="FoodBox",
            what_is_it="food delivery",
            topic="food",
            features=["fast", "cheap"],
            promo_code="SAVE10",
            promo_benefit="10% off",
            do_not_mention=["competitors"]
        )
        assert brand.name == "FoodBox"
        assert brand.description == "food delivery"
        assert brand.context_hint == "food"  # topic mapped to context_hint
        assert len(brand.attributes) == 2
        assert brand.promo == {"code": "SAVE10", "benefit": "10% off"}
        assert brand.promo_code == "SAVE10"
        assert brand.constraints == ["competitors"]

    def test_brand_returns_subject(self):
        """Brand factory returns a Subject instance."""
        brand = Brand(name="Test", what_is_it="test")
        assert isinstance(brand, Subject)
        assert brand.type == "brand"

    def test_brand_new_style_fields(self):
        """Brand also accepts new-style field names."""
        brand = Brand(
            name="FoodBox",
            description="food delivery",
            attributes=["fast", "cheap"],
            constraints=["competitors"]
        )
        assert brand.name == "FoodBox"
        assert brand.description == "food delivery"
        assert brand.attributes == ["fast", "cheap"]
        assert brand.constraints == ["competitors"]


class TestCampaign:
    """Tests for Campaign model."""

    def test_default_campaign(self):
        """Campaign has sensible defaults."""
        campaign = Campaign()
        assert campaign.goal == "awareness"
        assert campaign.style == "casual"
        assert campaign.mention_type == "natural"
        assert campaign.include_promo is False
        assert campaign.urgency is False

    def test_custom_campaign(self):
        """Campaign can be customized."""
        campaign = Campaign(
            goal="conversion",
            style="enthusiastic",
            mention_type="personal_experience",
            include_promo=True
        )
        assert campaign.goal == "conversion"
        assert campaign.style == "enthusiastic"
        assert campaign.mention_type == "personal_experience"
        assert campaign.include_promo is True

    def test_campaign_backward_compat(self):
        """Campaign accepts old brand_mention_type field."""
        campaign = Campaign(brand_mention_type="recommendation")
        assert campaign.mention_type == "recommendation"


class TestDialogContext:
    """Tests for DialogContext model."""

    def test_empty_context(self):
        """Context can be empty."""
        context = DialogContext()
        assert context.messages == []
        assert context.topic is None

    def test_context_with_messages(self):
        """Context can contain messages."""
        context = DialogContext(
            messages=[
                {"role": "person1", "content": "hello"},
                {"role": "person2", "content": "hi there"}
            ],
            topic="greeting"
        )
        assert len(context.messages) == 2
        assert context.topic == "greeting"


class TestDialogMessage:
    """Tests for DialogMessage model."""

    def test_message_required_fields(self):
        """Message requires role and content."""
        msg = DialogMessage(role="person1", content="hello")
        assert msg.role == "person1"
        assert msg.content == "hello"
        assert msg.delay_hint is None

    def test_message_with_delay(self):
        """Message can have delay hint."""
        msg = DialogMessage(role="person1", content="hi", delay_hint=2.5)
        assert msg.delay_hint == 2.5


class TestGeneratedDialog:
    """Tests for GeneratedDialog model."""

    def test_generated_dialog(self):
        """GeneratedDialog contains messages and metadata."""
        dialog = GeneratedDialog(
            messages=[DialogMessage(role="person1", content="test")],
            model_used="test-model",
            generation_params={"temperature": 0.8}
        )
        assert len(dialog.messages) == 1
        assert dialog.model_used == "test-model"
        assert dialog.generation_params["temperature"] == 0.8


class TestGenerateRequest:
    """Tests for GenerateRequest model."""

    def test_request_with_subject(self):
        """Request can be created with subject."""
        request = GenerateRequest(
            subject=Subject(name="Test", description="test")
        )
        assert request.subject.name == "Test"
        assert request.num_turns == 4  # default
        assert request.language == "ru"  # default
        assert request.campaign is not None  # default campaign

    def test_request_with_brand(self):
        """Request can be created with brand (backward compat)."""
        request = GenerateRequest(
            brand=Brand(name="Test", what_is_it="test")
        )
        assert request.subject.name == "Test"
        assert request.subject.description == "test"

    def test_full_request(self):
        """Request can have all fields."""
        request = GenerateRequest(
            subject=Subject(name="Test", description="test", type="topic"),
            campaign=Campaign(goal="trial"),
            context=DialogContext(messages=[{"role": "person1", "content": "hi"}]),
            num_turns=6,
            model="custom-model",
            temperature=0.9,
            language="en"
        )
        assert request.num_turns == 6
        assert request.model == "custom-model"
        assert request.temperature == 0.9
        assert request.language == "en"
        assert request.subject.type == "topic"

    def test_requires_subject_or_brand(self):
        """Request must have either subject or brand."""
        with pytest.raises(ValueError, match="subject.*brand"):
            GenerateRequest(num_turns=4)

    def test_num_turns_validation(self):
        """num_turns must be between 1 and 20."""
        with pytest.raises(ValueError):
            GenerateRequest(
                subject=Subject(name="Test", description="test"),
                num_turns=0
            )
        with pytest.raises(ValueError):
            GenerateRequest(
                subject=Subject(name="Test", description="test"),
                num_turns=25
            )

    def test_temperature_validation(self):
        """Temperature must be between 0 and 2."""
        with pytest.raises(ValueError):
            GenerateRequest(
                subject=Subject(name="Test", description="test"),
                temperature=-0.5
            )
        with pytest.raises(ValueError):
            GenerateRequest(
                subject=Subject(name="Test", description="test"),
                temperature=2.5
            )


class TestSingleResponseRequest:
    """Tests for SingleResponseRequest model."""

    def test_with_subject(self):
        """SingleResponseRequest works with subject."""
        request = SingleResponseRequest(
            subject=Subject(name="Test", description="test"),
            context=DialogContext(messages=[{"role": "person1", "content": "hi"}])
        )
        assert request.subject.name == "Test"
        assert len(request.context.messages) == 1

    def test_with_brand(self):
        """SingleResponseRequest works with brand (backward compat)."""
        request = SingleResponseRequest(
            brand=Brand(name="Test", what_is_it="test"),
            context=DialogContext(messages=[{"role": "person1", "content": "hi"}])
        )
        assert request.subject.name == "Test"
        assert len(request.context.messages) == 1


class TestModelInfo:
    """Tests for ModelInfo model."""

    def test_minimal_info(self):
        """ModelInfo needs only name."""
        info = ModelInfo(name="test-model")
        assert info.name == "test-model"
        assert info.size is None

    def test_full_info(self):
        """ModelInfo can have all fields."""
        info = ModelInfo(
            name="hermes3:8b",
            size="4.5GB",
            modified_at="2024-01-01",
            digest="abc123"
        )
        assert info.size == "4.5GB"


class TestCompareRequest:
    """Tests for CompareRequest model."""

    def test_with_subject(self):
        """CompareRequest works with subject."""
        request = CompareRequest(
            subject=Subject(name="Test", description="test", type="topic"),
            models=["model1", "model2"]
        )
        assert request.subject.name == "Test"
        assert request.subject.type == "topic"
        assert len(request.models) == 2
        assert request.num_turns == 4  # default

    def test_with_brand(self):
        """CompareRequest works with brand (backward compat)."""
        request = CompareRequest(
            brand=Brand(name="Test", what_is_it="test"),
            models=["model1", "model2"]
        )
        assert request.subject.name == "Test"
        assert len(request.models) == 2


class TestCompareResult:
    """Tests for CompareResult model."""

    def test_compare_result(self):
        """CompareResult contains dialog and timing."""
        result = CompareResult(
            model="test-model",
            dialog=GeneratedDialog(
                messages=[],
                model_used="test-model",
                generation_params={}
            ),
            generation_time_ms=1500
        )
        assert result.model == "test-model"
        assert result.generation_time_ms == 1500
