# Feature: Subject Types

## Overview

Flexible subject model supporting 6 types for different use cases: marketing, topic injection, information seeding, and event mentions.

## Subject Types

| Type | Use Case | Mention Style (RU) | Mention Style (EN) |
|------|----------|-------------------|-------------------|
| `brand` | Marketing, product placement | "Упомяни мимоходом, как личный опыт" | "Mention casually, as personal experience" |
| `product` | Specific product mentions | "Упомяни естественно, как покупку" | "Mention naturally, as a purchase" |
| `service` | Service recommendations | "Упомяни мимоходом, как опыт использования" | "Mention casually, as personal experience" |
| `topic` | News, trends, discussions | "Затроньте тему естественно" | "Touch on the topic naturally" |
| `info` | Facts, information seeding | "Включи информацию в диалог" | "Include information in the dialog" |
| `event` | Events, conferences | "Упомяни событие в контексте" | "Mention the event in context" |

## Functional Requirements

### FR-ST-001: Subject Model Fields
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| name | string | Yes | - | Subject name |
| description | string | Yes | - | What it is |
| type | string | No | "brand" | One of 6 types |
| attributes | string[] | No | [] | Key points to mention |
| constraints | string[] | No | [] | What NOT to mention |
| mention_style | string | No | "natural" | How to mention |
| context_hint | string | No | null | Extra context for LLM |
| promo | object | No | null | {code, benefit} |

### FR-ST-002: Type Labels (Localized)
System MUST provide localized labels for each type:

| Type | Russian | English |
|------|---------|---------|
| brand | БРЕНД | BRAND |
| product | ПРОДУКТ | PRODUCT |
| service | СЕРВИС | SERVICE |
| topic | ТЕМА | TOPIC |
| info | ИНФОРМАЦИЯ | INFO |
| event | СОБЫТИЕ | EVENT |

### FR-ST-003: Mention Instructions
Each type has language-specific mention instructions that guide LLM behavior.

### FR-ST-004: Backward Compatibility
- `Brand()` factory function MUST work with legacy field names
- Field mappings:
  - `what_is_it` → `description`
  - `features` → `attributes`
  - `do_not_mention` → `constraints`
  - `topic` → `context_hint`
  - `promo_code`/`promo_benefit` → `promo` dict

## Usage Examples

### Brand (Marketing)
```python
Subject(
    name="FoodBox",
    description="food delivery service",
    type="brand",
    attributes=["fast delivery", "many restaurants"]
)
```

### Topic (News)
```python
Subject(
    name="Bitcoin ETF",
    description="investment news",
    type="topic",
    attributes=["SEC approved", "institutional adoption"]
)
```

### Info (Facts)
```python
Subject(
    name="Python 3.13",
    description="new features",
    type="info",
    attributes=["GIL removal", "JIT compiler"]
)
```

## Code Reference (ast-grep)

### Classes
- `class Subject` - Core subject model with 6 types
- `class Brand` - Legacy alias (factory function returns Subject)

### Key Functions
- `def Brand($$$) -> Subject` - Factory function for backward compatibility
- `def get_type_label(self, language: str) -> str` - Get localized type label
- `def get_mention_instruction(self, language: str) -> str` - Get localized mention instruction

### Properties
- `Subject.name` - Subject name
- `Subject.description` - What it is
- `Subject.type` - One of: brand, product, service, topic, info, event
- `Subject.attributes` - List of key points to mention
- `Subject.constraints` - List of things NOT to mention
- `Subject.context_hint` - Extra context for LLM
- `Subject.promo_code` - Promotional code
- `Subject.promo_benefit` - Promo benefit description

## Verification Criteria

- [ ] All 6 types produce distinct prompt content
- [ ] Type labels appear correctly in prompts
- [ ] Mention instructions vary by type
- [ ] Legacy Brand() syntax works
- [ ] Attributes included in system prompt

## Related

- [Multi-Language](./feature-multi-language.md)
- [Data Model](../architecture/data-model.md)
- [ADR-001: Subject over Brand](../decisions/ADR-001-subject-over-brand.md)
