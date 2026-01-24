# Feature: Multi-Language Support

## Overview

Full support for Russian and English dialog generation with language-specific prompts, style rules, and mention instructions.

## Supported Languages

| Code | Language | Default |
|------|----------|---------|
| `ru` | Russian | Yes |
| `en` | English | No |

## Functional Requirements

### FR-ML-001: Language Selection
- `language` parameter in all generation requests
- Default: `ru` (from settings)
- CLI: `--lang` / `-l` flag

### FR-ML-002: Localized System Prompts
Each language has dedicated prompt templates:

**Russian (`ru`)**
- `system_prefix`: Conversation setup in Russian
- `style_rules`: Russian texting style guidelines
- `negative_examples`: What NOT to do (Russian)
- `brand_mention`: Natural mention guidelines

**English (`en`)**
- `system_prefix`: Conversation setup in English
- `style_rules`: Texting style guidelines

### FR-ML-003: Localized Type Labels
Subject type labels adapted per language (see [Subject Types](./feature-subject-types.md)).

### FR-ML-004: Localized Mention Instructions
Each subject type has language-specific mention instructions.

## Prompt Structure (Russian)

```
{system_prefix}

БРЕНД для упоминания: {name} ({description})
Особенности: {attributes}
НЕ упоминай: {constraints}

{style_rules}
{negative_examples}
{mention_instruction}
```

## Prompt Structure (English)

```
{system_prefix}

BRAND: {name}
What it is: {description}
Features: {attributes}
DO NOT mention: {constraints}

GOAL: {campaign.goal}
STYLE: {campaign.style}
HOW TO MENTION: {campaign.mention_type}

{style_rules}
```

## Configuration

```json
{
  "style": {
    "language": "ru"
  },
  "prompts": {
    "ru": {
      "system_prefix": "...",
      "style_rules": "...",
      "negative_examples": "...",
      "brand_mention": "..."
    },
    "en": {
      "system_prefix": "...",
      "style_rules": "..."
    }
  }
}
```

## Code Reference (ast-grep)

### Classes
- `class RuPrompts` - Russian prompt templates
- `class EnPrompts` - English prompt templates
- `class PromptsConfig` - Combined prompts configuration

### Key Functions
- `def get_prompt(self, language: str, key: str) -> str` - Get localized prompt template
- `def get_type_label(self, language: str) -> str` - Get localized type label (in Subject)
- `def get_mention_instruction(self, language: str) -> str` - Get localized mention instruction (in Subject)
- `def _build_system_prompt(self, subject, campaign, language: str) -> str` - Build language-specific system prompt

### Properties
- `RuPrompts.system_prefix` - Russian system prompt prefix
- `RuPrompts.style_rules` - Russian style rules
- `RuPrompts.negative_examples` - Russian negative examples
- `RuPrompts.brand_mention` - Russian brand mention instruction
- `EnPrompts.system_prefix` - English system prompt prefix
- `EnPrompts.style_rules` - English style rules
- `GenerateRequest.language` - Request language code ("ru" or "en")

## Verification Criteria

- [ ] Russian prompts use Cyrillic text
- [ ] English prompts use English text
- [ ] Type labels change with language
- [ ] Generated dialog matches selected language
- [ ] Style rules appropriate for each language

## Related

- [Subject Types](./feature-subject-types.md)
- [Configuration](./feature-configuration.md)
- [ADR-004: Multi-Language Prompts](../decisions/ADR-004-multi-language-prompts.md)
