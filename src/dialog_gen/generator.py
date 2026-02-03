"""
Dialog generation engine.

Generates natural Telegram-style conversations with brand mentions
using cloud LLMs via OpenRouter.
"""

import logging
import re
import time
import random
import json
from typing import Optional

from .cloud_client import get_cloud_client

logger = logging.getLogger(__name__)
from .settings import settings
from .models import (
    Subject, Brand, Campaign, DialogContext, DialogMessage, GeneratedDialog,
    GenerateRequest, SingleResponseRequest
)


class DialogGenerator:
    """Generates natural dialogs using LLMs via OpenRouter.

    The generator creates realistic chat conversations that naturally
    incorporate brand mentions based on the provided context and settings.

    Attributes:
        model: The LLM model to use for generation.
        provider: Always 'openrouter'.

    Example:
        >>> generator = DialogGenerator()
        >>> request = GenerateRequest(
        ...     brand=Brand(name="FoodBox", what_is_it="food delivery"),
        ...     num_turns=4
        ... )
        >>> result = await generator.generate_dialog(request)
        >>> for msg in result.messages:
        ...     print(f"{msg.role}: {msg.content}")
    """

    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None):
        """Initialize the generator.

        Args:
            model: LLM model name. Defaults to settings.cloud.openrouter_model.
            provider: Ignored, always uses OpenRouter.
        """
        self.provider = "openrouter"
        self.model = model or settings.cloud.openrouter_model

    def _build_system_prompt(self, subject: Subject, campaign: Campaign, language: str) -> str:
        """Build system prompt from subject, campaign, and language settings.

        Args:
            subject: Subject information to mention (brand, topic, info, etc.).
            campaign: Campaign settings for tone and style.
            language: Language code ('ru' or 'en').

        Returns:
            Complete system prompt string.
        """
        # Get localized type label
        type_label = subject.get_type_label(language)

        if language == "ru":
            prompt = f"{settings.get_prompt('ru', 'system_prefix')}\n\n"
            prompt += f"{type_label} для упоминания: {subject.name} ({subject.description})\n"

            if subject.attributes:
                if subject.type in ("brand", "product", "service"):
                    prompt += f"Особенности: {', '.join(subject.attributes)}\n"
                else:
                    prompt += f"Ключевые моменты: {', '.join(subject.attributes)}\n"

            if subject.context_hint:
                prompt += f"Контекст: {subject.context_hint}\n"

            if subject.constraints:
                prompt += f"НЕ упоминай: {', '.join(subject.constraints)}\n"

            prompt += f"\n{settings.get_prompt('ru', 'style_rules')}\n"
            prompt += f"\n{settings.get_prompt('ru', 'negative_examples')}\n"
            prompt += f"\n{subject.get_mention_instruction(language)}"

        else:  # English
            prompt = f"{settings.get_prompt('en', 'system_prefix')}\n\n"
            prompt += f"{type_label}: {subject.name}\n"
            prompt += f"What it is: {subject.description}\n"

            if subject.attributes:
                if subject.type in ("brand", "product", "service"):
                    prompt += f"Features: {', '.join(subject.attributes)}\n"
                else:
                    prompt += f"Key points: {', '.join(subject.attributes)}\n"

            if subject.context_hint:
                prompt += f"Context: {subject.context_hint}\n"

            if subject.promo_code and campaign.include_promo:
                prompt += f"Promo code: {subject.promo_code}"
                if subject.promo_benefit:
                    prompt += f" ({subject.promo_benefit})"
                prompt += "\n"

            if subject.constraints:
                prompt += f"DO NOT mention: {', '.join(subject.constraints)}\n"

            prompt += f"\nGOAL: {campaign.goal}\n"
            prompt += f"STYLE: {campaign.style}\n"
            prompt += f"HOW TO MENTION: {campaign.mention_type}\n"
            prompt += f"\n{settings.get_prompt('en', 'style_rules')}"

        return prompt

    def _build_generation_prompt(
        self,
        subject: Subject,
        campaign: Campaign,
        num_turns: int,
        context: Optional[DialogContext],
        language: str
    ) -> str:
        """Build the user prompt for dialog generation.

        Args:
            subject: Subject to mention.
            campaign: Campaign settings.
            num_turns: Number of messages to generate.
            context: Optional conversation context to continue.
            language: Language code.

        Returns:
            Generation prompt string.
        """
        # Get the mention instruction based on subject type
        mention_instruction = subject.get_mention_instruction(language)

        if language == "ru":
            prompt = ""

            if context and context.messages:
                # Calculate message length stats for style matching
                lengths = [len(m['content']) for m in context.messages]
                avg_len = sum(lengths) // len(lengths)
                max_len = max(lengths)

                prompt += "Чат:\n"
                for msg in context.messages[-10:]:
                    prompt += f"{msg['role']}: {msg['content']}\n"

                prompt += f"""
Продолжи. {num_turns} сообщений. {mention_instruction}

ДЛИНА СООБЩЕНИЙ: максимум {max_len} символов! В среднем ~{avg_len}.
Короткие фразы как выше. Без длинных предложений.

JSON: [{{"role": "person1", "text": "короткое"}}, {{"role": "person2", "text": "тоже короткое"}}]"""

            else:
                prompt = f"Напиши {num_turns} коротких сообщений чата. {mention_instruction}\n"
                prompt += f'JSON: [{{"role": "person1", "text": "..."}}, {{"role": "person2", "text": "..."}}]'

        else:  # English
            prompt = f"Write {num_turns} chat messages.\n\n"

            if context:
                if context.topic:
                    prompt += f"Topic: {context.topic}\n"
                if context.setting:
                    prompt += f"Setting: {context.setting}\n"
                if context.messages:
                    prompt += "Previous messages:\n"
                    for msg in context.messages[-5:]:
                        prompt += f"{msg['role']}: {msg['content']}\n"
                    prompt += "\nContinue this conversation:\n"

            prompt += f"""
Output format - JSON array:
[
  {{"role": "person1", "text": "message"}},
  {{"role": "person2", "text": "reply"}}
]

IMPORTANT:
- {mention_instruction}
- Write exactly {num_turns} messages
- Write like real chat, not advertisement"""

        return prompt

    def _parse_dialog(self, raw_text: str) -> list[DialogMessage]:
        """Parse LLM output into dialog messages.

        Handles various output formats including JSON arrays and plain text.

        Args:
            raw_text: Raw LLM output.

        Returns:
            List of parsed DialogMessage objects.
        """
        messages = []
        text = raw_text.strip()

        # Try to find JSON array in response
        start = text.find('[')
        end = text.rfind(']') + 1

        if start == -1 or end == 0:
            return self._parse_dialog_lines(text)

        try:
            json_str = text[start:end]
            # Fix common JSON errors from LLMs
            json_str = json_str.replace("\\n", " ")
            json_str = re.sub(r',\s*]', ']', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)

            data = json.loads(json_str)

            for item in data:
                if isinstance(item, str):
                    messages.append(DialogMessage(
                        role=f"person{len(messages) % 3 + 1}",
                        content=item,
                        delay_hint=self._calculate_delay(item)
                    ))
                    continue

                role = item.get("role", f"person{len(messages) % 3 + 1}")
                # Normalize old sender/responder format
                if role == "sender":
                    role = "person1"
                elif role == "responder":
                    role = "person2"

                content = item.get("text", item.get("content", item.get("message", "")))

                # Skip placeholder text
                if not content or content in ["сообщение", "ответ", "реальное сообщение", "реальный ответ"]:
                    continue

                messages.append(DialogMessage(
                    role=role,
                    content=content,
                    delay_hint=self._calculate_delay(content)
                ))

        except json.JSONDecodeError:
            return self._parse_dialog_lines(text)

        return messages

    def _parse_dialog_lines(self, raw_text: str) -> list[DialogMessage]:
        """Fallback parser for non-JSON output.

        Args:
            raw_text: Raw text to parse.

        Returns:
            List of DialogMessage objects.
        """
        messages = []
        text = raw_text.strip()

        # Try to find JSON objects in text
        json_pattern = r'\{"role":\s*"(sender|responder|person\d+)",\s*"text":\s*"([^"]+)"\}'
        json_matches = re.findall(json_pattern, text)

        if json_matches:
            for role, content in json_matches:
                if content and content not in ["сообщение", "ответ"]:
                    # Normalize old format
                    if role == "sender":
                        role = "person1"
                    elif role == "responder":
                        role = "person2"
                    messages.append(DialogMessage(
                        role=role,
                        content=content,
                        delay_hint=self._calculate_delay(content)
                    ))
            return messages

        # Parse line by line
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for line in lines:
            if line in ['[', ']', '{', '}']:
                continue

            match = re.match(r'^[A-Za-zА-Яа-яЁё_\-0-9]+:\s*(.+)$', line)
            content = match.group(1) if match else line

            if content.startswith('{') or content.startswith('"role"'):
                continue

            role = f"person{len(messages) % 3 + 1}"
            messages.append(DialogMessage(
                role=role,
                content=content,
                delay_hint=self._calculate_delay(content)
            ))

        return messages

    def _calculate_delay(self, message: str) -> float:
        """Calculate realistic typing delay for a message.

        Args:
            message: Message text.

        Returns:
            Delay in seconds.
        """
        word_count = len(message.split())
        base_delay = word_count * 1.5
        jitter = random.uniform(0.8, 1.2)
        return round(min(base_delay * jitter, 30.0), 1)

    async def _call_llm(
        self,
        model: str,
        prompt: str,
        system: str,
        temperature: float,
        provider: Optional[str] = None
    ) -> str:
        """Call LLM via OpenRouter.

        Args:
            model: Model name.
            prompt: User prompt.
            system: System prompt.
            temperature: Temperature setting.
            provider: Ignored, always uses OpenRouter.

        Returns:
            Generated text.
        """
        cloud = get_cloud_client()
        return await cloud.generate(
            model=model,
            prompt=prompt,
            system=system,
            temperature=temperature,
            top_p=settings.top_p,
            max_tokens=settings.max_tokens,
        )

    async def generate_dialog(self, request: GenerateRequest) -> GeneratedDialog:
        """Generate a complete dialog.

        Args:
            request: Generation request with subject, campaign, and settings.

        Returns:
            GeneratedDialog with messages and metadata.
        """
        model = request.model or self.model
        temperature = request.temperature or settings.temperature

        system_prompt = self._build_system_prompt(
            request.subject, request.campaign, request.language
        )
        generation_prompt = self._build_generation_prompt(
            request.subject,
            request.campaign,
            request.num_turns,
            request.context,
            request.language
        )

        logger.info(
            "Generating dialog: model=%s, num_turns=%d, language=%s, temperature=%s, subject=%s",
            model, request.num_turns, request.language, temperature, request.subject.name
        )
        logger.debug("System prompt:\n%s", system_prompt)
        logger.debug("Generation prompt:\n%s", generation_prompt)

        start_time = time.time()

        raw_response = await self._call_llm(
            model=model,
            prompt=generation_prompt,
            system=system_prompt,
            temperature=temperature
        )

        generation_time = int((time.time() - start_time) * 1000)

        logger.info("LLM response received: %dms, %d chars", generation_time, len(raw_response))
        logger.debug("Raw LLM response:\n%s", raw_response)

        messages = self._parse_dialog(raw_response)

        logger.info(
            "Dialog parsed: %d messages [%s]",
            len(messages),
            " | ".join(f"{m.role}: {m.content[:60]}..." if len(m.content) > 60 else f"{m.role}: {m.content}" for m in messages)
        )

        return GeneratedDialog(
            messages=messages,
            model_used=model,
            generation_params={
                "provider": self.provider,
                "temperature": temperature,
                "generation_time_ms": generation_time,
                "raw_response_length": len(raw_response),
                "system_prompt": system_prompt,
                "generation_prompt": generation_prompt,
                "raw_response": raw_response,
            }
        )

    async def generate_single_response(self, request: SingleResponseRequest) -> DialogMessage:
        """Generate a single response in conversation context.

        Args:
            request: Request with context and settings.

        Returns:
            Single DialogMessage response.
        """
        model = request.model or self.model
        temperature = request.temperature or settings.temperature

        system_prompt = self._build_system_prompt(
            request.subject, request.campaign, request.language
        )

        history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in request.context.messages
        ])

        # Determine next speaker
        if request.context.messages:
            last_role = request.context.messages[-1].get("role", "")
            match = re.match(r'person(\d+)', last_role)
            if match:
                next_num = int(match.group(1)) % 3 + 1
                next_role = f"person{next_num}"
            else:
                next_role = "person1" if last_role == "person2" else "person2"
        else:
            next_role = "person1"

        prompt = f"""Продолжи этот разговор. Напиши следующее сообщение от {next_role}.

Предыдущие сообщения:
{history}

Напиши только одно сообщение:"""

        logger.info(
            "Generating single response: model=%s, next_role=%s, context_messages=%d",
            model, next_role, len(request.context.messages)
        )
        logger.debug("System prompt:\n%s", system_prompt)
        logger.debug("Response prompt:\n%s", prompt)

        raw_response = await self._call_llm(
            model=model,
            prompt=prompt,
            system=system_prompt,
            temperature=temperature
        )

        logger.debug("Raw LLM response:\n%s", raw_response)

        content = raw_response.strip()
        content = re.sub(r'^(SENDER|RESPONDER|sender|responder|person\d+|PERSON\d+):\s*', '', content)

        return DialogMessage(
            role=next_role,
            content=content,
            delay_hint=self._calculate_delay(content)
        )


# Global generator instance
generator = DialogGenerator()
