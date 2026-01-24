"""Tests for dialog generator."""

import pytest
from unittest.mock import AsyncMock, patch
from dialog_gen.generator import DialogGenerator
from dialog_gen.models import (
    Subject, Brand, Campaign, DialogContext, DialogMessage,
    GenerateRequest, SingleResponseRequest
)


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


class TestGenerateDialog:
    """Tests for generate_dialog async method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator(model="test-model", provider="ollama")

    @pytest.fixture
    def subject(self):
        return Subject(name="FoodBox", description="food delivery", type="brand")

    @pytest.fixture
    def gen_request(self, subject):
        return GenerateRequest(subject=subject, num_turns=4, language="ru")

    @pytest.mark.asyncio
    async def test_generate_dialog_returns_generated_dialog(self, generator, gen_request):
        """generate_dialog returns GeneratedDialog with messages."""
        mock_response = '''[
            {"role": "person1", "text": "Привет!"},
            {"role": "person2", "text": "Привет, как дела?"},
            {"role": "person1", "text": "Хорошо, заказал еду в FoodBox"},
            {"role": "person2", "text": "О, слышал про них!"}
        ]'''

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            result = await generator.generate_dialog(gen_request)

        assert result is not None
        assert len(result.messages) == 4
        assert result.model_used == "test-model"
        assert "generation_time_ms" in result.generation_params

    @pytest.mark.asyncio
    async def test_generate_dialog_with_context(self, generator, subject):
        """generate_dialog works with context."""
        context = DialogContext(messages=[
            {"role": "person1", "content": "Привет"},
            {"role": "person2", "content": "Привет!"}
        ])
        request = GenerateRequest(
            subject=subject,
            context=context,
            num_turns=2,
            language="ru"
        )

        mock_response = '''[
            {"role": "person1", "text": "Что делаешь?"},
            {"role": "person2", "text": "Заказываю еду"}
        ]'''

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            result = await generator.generate_dialog(request)

        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_generate_dialog_custom_temperature(self, generator, subject):
        """generate_dialog uses custom temperature."""
        request = GenerateRequest(
            subject=subject,
            num_turns=2,
            temperature=0.5
        )

        mock_response = '[{"role": "person1", "text": "Test"}]'

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response
            await generator.generate_dialog(request)

            # Verify temperature was passed
            call_kwargs = mock_llm.call_args.kwargs
            assert call_kwargs.get('temperature') == 0.5

    @pytest.mark.asyncio
    async def test_generate_dialog_handles_empty_response(self, generator, gen_request):
        """generate_dialog handles empty LLM response gracefully."""
        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "[]"
            result = await generator.generate_dialog(gen_request)

        assert result.messages == []


class TestGenerateSingleResponse:
    """Tests for generate_single_response async method."""

    @pytest.fixture
    def generator(self):
        return DialogGenerator(model="test-model", provider="ollama")

    @pytest.fixture
    def subject(self):
        return Subject(name="FoodBox", description="food delivery", type="brand")

    @pytest.fixture
    def context(self):
        return DialogContext(messages=[
            {"role": "person1", "content": "Привет"},
            {"role": "person2", "content": "Привет, как дела?"}
        ])

    @pytest.mark.asyncio
    async def test_single_response_returns_message(self, generator, subject, context):
        """generate_single_response returns a DialogMessage."""
        request = SingleResponseRequest(
            subject=subject,
            context=context,
            campaign=Campaign()
        )

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Нормально, работаю!"
            result = await generator.generate_single_response(request)

        assert isinstance(result, DialogMessage)
        assert result.content == "Нормально, работаю!"
        assert result.role == "person3"  # Next after person2 (2 % 3 + 1 = 3)

    @pytest.mark.asyncio
    async def test_single_response_strips_role_prefix(self, generator, subject, context):
        """generate_single_response strips role prefix from response."""
        request = SingleResponseRequest(
            subject=subject,
            context=context,
            campaign=Campaign()
        )

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "person1: Хорошо!"
            result = await generator.generate_single_response(request)

        assert result.content == "Хорошо!"

    @pytest.mark.asyncio
    async def test_single_response_cycles_roles(self, generator, subject):
        """generate_single_response cycles through roles correctly."""
        # After person3, should go back to person1
        context = DialogContext(messages=[
            {"role": "person1", "content": "First"},
            {"role": "person2", "content": "Second"},
            {"role": "person3", "content": "Third"}
        ])
        request = SingleResponseRequest(
            subject=subject,
            context=context,
            campaign=Campaign()
        )

        with patch.object(generator, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Fourth"
            result = await generator.generate_single_response(request)

        assert result.role == "person1"  # Cycles back


class TestCallLlm:
    """Tests for _call_llm method."""

    @pytest.mark.asyncio
    async def test_call_llm_auto_detects_openai(self):
        """_call_llm auto-detects OpenAI provider."""
        generator = DialogGenerator(provider="auto")

        with patch('dialog_gen.generator.get_cloud_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "response"
            mock_get_client.return_value = mock_client

            result = await generator._call_llm(
                model="gpt-4o-mini",
                prompt="test",
                system="system",
                temperature=0.8
            )

            mock_client.generate.assert_called_once()
            call_kwargs = mock_client.generate.call_args.kwargs
            assert call_kwargs['provider'] == 'openai'

    @pytest.mark.asyncio
    async def test_call_llm_auto_detects_anthropic(self):
        """_call_llm auto-detects Anthropic provider."""
        generator = DialogGenerator(provider="auto")

        with patch('dialog_gen.generator.get_cloud_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "response"
            mock_get_client.return_value = mock_client

            await generator._call_llm(
                model="haiku",
                prompt="test",
                system="system",
                temperature=0.8
            )

            call_kwargs = mock_client.generate.call_args.kwargs
            assert call_kwargs['provider'] == 'anthropic'

    @pytest.mark.asyncio
    async def test_call_llm_uses_ollama_by_default(self):
        """_call_llm uses Ollama for unknown models."""
        generator = DialogGenerator(provider="auto")

        with patch('dialog_gen.generator.ollama') as mock_ollama:
            mock_ollama.generate = AsyncMock(return_value="response")

            await generator._call_llm(
                model="hermes3:8b",
                prompt="test",
                system="system",
                temperature=0.8
            )

            mock_ollama.generate.assert_called_once()
