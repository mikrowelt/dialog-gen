# ADR-004: Language-specific Prompt Templates

## Status

Accepted

## Context

The dialog generator supports multiple languages (Russian, English). Initially, prompts were hardcoded in Russian:

```python
prompt = f"БРЕНД: {brand.name}\n"
prompt += "Упомяни бренд мимоходом..."
```

This approach:
- Made English dialogs unnatural
- Couldn't adapt terminology per language
- Mixed language in prompts confused LLMs

## Decision

Implement language-aware prompt templates using dictionaries:

### Type Labels

```python
SUBJECT_TYPE_LABELS = {
    "ru": {
        "brand": "БРЕНД",
        "product": "ПРОДУКТ",
        "topic": "ТЕМА",
        "info": "ИНФОРМАЦИЯ",
        "event": "СОБЫТИЕ"
    },
    "en": {
        "brand": "BRAND",
        "product": "PRODUCT",
        "topic": "TOPIC",
        "info": "INFO",
        "event": "EVENT"
    }
}
```

### Mention Instructions

```python
MENTION_INSTRUCTIONS = {
    "ru": {
        "brand": "Упомяни {name} мимоходом, как личный опыт",
        "topic": "Затроньте тему {name} естественно в разговоре",
        "info": "Включи информацию о {name} в диалог"
    },
    "en": {
        "brand": "Mention {name} casually, as personal experience",
        "topic": "Touch on the topic of {name} naturally in conversation",
        "info": "Include information about {name} in the dialog"
    }
}
```

### Subject Methods

```python
class Subject(BaseModel):
    def get_type_label(self, language: str = "ru") -> str:
        labels = SUBJECT_TYPE_LABELS.get(language, SUBJECT_TYPE_LABELS["en"])
        return labels.get(self.type, self.type.upper())

    def get_mention_instruction(self, language: str = "ru") -> str:
        instructions = MENTION_INSTRUCTIONS.get(language, MENTION_INSTRUCTIONS["en"])
        template = instructions.get(self.type, instructions.get("brand", ""))
        return template.format(name=self.name)
```

## Consequences

### Positive

- **Native feel**: Prompts match output language
- **LLM clarity**: No mixed-language confusion
- **Extensibility**: Easy to add new languages
- **Type-specific**: Each subject type has tailored instructions

### Negative

- **Maintenance**: Must keep translations in sync
- **Fallbacks**: Need graceful handling of missing translations

### Fallback Strategy

1. Unknown language → Fall back to English
2. Unknown type → Fall back to `brand` instructions
3. Missing template → Return empty string (safe default)

## Usage

```python
# In generator.py
label = subject.get_type_label(language)  # "БРЕНД" or "BRAND"
instruction = subject.get_mention_instruction(language)

prompt = f"{label}: {subject.name}\n"
prompt += f"{instruction}\n"
```

## Related

- [ADR-001: Subject over Brand](./ADR-001-subject-over-brand.md)
- [Multi-language Feature](../requirements/feature-multi-language.md)
- [Generator Architecture](../architecture/generator.md)
