"""Tests for dialog generator."""

import pytest
from dialog_gen.generator import DialogGenerator
from dialog_gen.models import Subject, Brand, Campaign, DialogContext, DialogMessage


class TestDialogGenerator:
    """Tests for DialogGenerator class."""

    def test_init_default_model(self):
        """Generator uses default model from settings."""
        generator = DialogGenerator()
        assert generator.model is not None

    def test_init_custom_model(self):
        """Generator accepts custom model."""
        generator = DialogGenerator(model="custom:latest")
        assert generator.model == "custom:latest"


class TestBuildSystemPrompt:
    """Tests for _build_system_prompt method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator()

    @pytest.fixture
    def subject(self):
        return Subject(
            name="FoodBox",
            description="food delivery service",
            type="brand",
            attributes=["fast delivery", "many restaurants"],
            constraints=["competitors"]
        )

    @pytest.fixture
    def topic_subject(self):
        return Subject(
            name="Bitcoin ETF",
            description="investment news",
            type="topic",
            attributes=["SEC approved", "major milestone"]
        )

    @pytest.fixture
    def campaign(self):
        return Campaign()

    def test_ru_prompt_contains_subject(self, generator, subject, campaign):
        """Russian prompt contains subject info."""
        prompt = generator._build_system_prompt(subject, campaign, "ru")
        assert "FoodBox" in prompt
        assert "food delivery" in prompt

    def test_ru_prompt_contains_type_label(self, generator, subject, topic_subject, campaign):
        """Russian prompt contains correct type label."""
        brand_prompt = generator._build_system_prompt(subject, campaign, "ru")
        topic_prompt = generator._build_system_prompt(topic_subject, campaign, "ru")
        assert "БРЕНД" in brand_prompt
        assert "ТЕМА" in topic_prompt

    def test_ru_prompt_contains_attributes(self, generator, subject, campaign):
        """Russian prompt contains attributes."""
        prompt = generator._build_system_prompt(subject, campaign, "ru")
        assert "fast delivery" in prompt

    def test_ru_prompt_contains_constraints(self, generator, subject, campaign):
        """Russian prompt contains constraints."""
        prompt = generator._build_system_prompt(subject, campaign, "ru")
        assert "competitors" in prompt

    def test_ru_prompt_contains_style_rules(self, generator, subject, campaign):
        """Russian prompt contains style rules from settings."""
        prompt = generator._build_system_prompt(subject, campaign, "ru")
        assert "СТИЛЬ" in prompt or "стиль" in prompt.lower()

    def test_en_prompt_contains_subject(self, generator, subject, campaign):
        """English prompt contains subject info."""
        prompt = generator._build_system_prompt(subject, campaign, "en")
        assert "FoodBox" in prompt
        assert "BRAND" in prompt

    def test_en_prompt_contains_type_label(self, generator, topic_subject, campaign):
        """English prompt contains correct type label for topic."""
        prompt = generator._build_system_prompt(topic_subject, campaign, "en")
        assert "TOPIC" in prompt
        assert "Bitcoin ETF" in prompt

    def test_en_prompt_contains_campaign_goal(self, generator, subject, campaign):
        """English prompt contains campaign goal."""
        prompt = generator._build_system_prompt(subject, campaign, "en")
        assert "GOAL" in prompt
        assert campaign.goal in prompt


class TestBuildGenerationPrompt:
    """Tests for _build_generation_prompt method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator()

    @pytest.fixture
    def subject(self):
        return Subject(name="FoodBox", description="food delivery", type="brand")

    @pytest.fixture
    def topic_subject(self):
        return Subject(name="Bitcoin ETF", description="investment news", type="topic")

    @pytest.fixture
    def campaign(self):
        return Campaign()

    def test_ru_prompt_without_context(self, generator, subject, campaign):
        """Russian prompt without context."""
        prompt = generator._build_generation_prompt(subject, campaign, 4, None, "ru")
        assert "FoodBox" in prompt
        assert "JSON" in prompt

    def test_ru_prompt_with_context(self, generator, subject, campaign):
        """Russian prompt with context includes length constraints."""
        context = DialogContext(
            messages=[
                {"role": "person1", "content": "привет"},
                {"role": "person2", "content": "привет, как дела?"}
            ]
        )
        prompt = generator._build_generation_prompt(subject, campaign, 4, context, "ru")
        assert "Чат:" in prompt
        assert "person1" in prompt
        assert "ДЛИНА" in prompt  # Length constraint

    def test_en_prompt_with_context(self, generator, subject, campaign):
        """English prompt with context."""
        context = DialogContext(
            messages=[{"role": "person1", "content": "hello"}],
            topic="greeting"
        )
        prompt = generator._build_generation_prompt(subject, campaign, 4, context, "en")
        assert "Topic: greeting" in prompt
        assert "person1: hello" in prompt

    def test_topic_type_uses_different_instruction(self, generator, topic_subject, campaign):
        """Topic type uses different mention instruction."""
        prompt_ru = generator._build_generation_prompt(topic_subject, campaign, 4, None, "ru")
        prompt_en = generator._build_generation_prompt(topic_subject, campaign, 4, None, "en")
        assert "тему" in prompt_ru.lower() or "bitcoin" in prompt_ru.lower()
        assert "topic" in prompt_en.lower() or "Bitcoin" in prompt_en


class TestParseDialog:
    """Tests for _parse_dialog method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator()

    def test_parse_json_array(self, generator):
        """Parses valid JSON array."""
        raw = '[{"role": "person1", "text": "hello"}, {"role": "person2", "text": "hi"}]'
        messages = generator._parse_dialog(raw)
        assert len(messages) == 2
        assert messages[0].role == "person1"
        assert messages[0].content == "hello"

    def test_parse_json_with_prefix(self, generator):
        """Parses JSON with text prefix."""
        raw = 'Here is the dialog:\n[{"role": "person1", "text": "hello"}]'
        messages = generator._parse_dialog(raw)
        assert len(messages) == 1

    def test_normalize_sender_responder(self, generator):
        """Normalizes old sender/responder format."""
        raw = '[{"role": "sender", "text": "hi"}, {"role": "responder", "text": "hello"}]'
        messages = generator._parse_dialog(raw)
        assert messages[0].role == "person1"
        assert messages[1].role == "person2"

    def test_skip_placeholder_text(self, generator):
        """Skips placeholder text like 'сообщение'."""
        raw = '[{"role": "person1", "text": "сообщение"}, {"role": "person2", "text": "real text"}]'
        messages = generator._parse_dialog(raw)
        assert len(messages) == 1
        assert messages[0].content == "real text"

    def test_parse_malformed_json(self, generator):
        """Handles malformed JSON gracefully."""
        raw = '[{"role": "person1", "text": "hello",}]'  # Trailing comma
        messages = generator._parse_dialog(raw)
        assert len(messages) == 1

    def test_parse_line_format(self, generator):
        """Parses line-by-line format."""
        raw = "person1: hello\nperson2: hi there"
        messages = generator._parse_dialog(raw)
        assert len(messages) == 2


class TestParseDialogLines:
    """Tests for _parse_dialog_lines fallback method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator()

    def test_parse_simple_lines(self, generator):
        """Parses simple role: content lines."""
        raw = "person1: hello\nperson2: hi"
        messages = generator._parse_dialog_lines(raw)
        assert len(messages) == 2
        assert messages[0].content == "hello"

    def test_skip_json_artifacts(self, generator):
        """Skips JSON brackets in output."""
        raw = "[\nperson1: hello\n]\n"
        messages = generator._parse_dialog_lines(raw)
        assert len(messages) == 1
        assert messages[0].content == "hello"

    def test_assigns_roles_cyclically(self, generator):
        """Assigns person1, person2, person3 cyclically."""
        raw = "first\nsecond\nthird\nfourth"
        messages = generator._parse_dialog_lines(raw)
        assert messages[0].role == "person1"
        assert messages[1].role == "person2"
        assert messages[2].role == "person3"
        assert messages[3].role == "person1"  # Cycles back


class TestCalculateDelay:
    """Tests for _calculate_delay method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator()

    def test_short_message(self, generator):
        """Short message has short delay."""
        delay = generator._calculate_delay("hi")
        assert delay < 5

    def test_long_message(self, generator):
        """Long message has longer delay."""
        long_msg = " ".join(["word"] * 20)
        delay = generator._calculate_delay(long_msg)
        assert delay > 10

    def test_max_delay(self, generator):
        """Delay is capped at 30 seconds."""
        very_long = " ".join(["word"] * 100)
        delay = generator._calculate_delay(very_long)
        assert delay <= 30
