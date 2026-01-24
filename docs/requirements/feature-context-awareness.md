# Feature: Context Awareness

## Overview

Continue existing conversations naturally by providing previous messages as context. Generated responses match the style and flow of the input conversation.

## Functional Requirements

### FR-CA-001: Context Input
- Accept previous messages via `DialogContext`
- Maximum 10 messages included in prompt (last 10)
- Each message has `role` and `content`

### FR-CA-002: Style Matching
When context is provided:
- Calculate average message length
- Calculate maximum message length
- Generated messages stay within observed limits
- Tone and formality match context

### FR-CA-003: Role Continuation
- Determine next speaker based on conversation history
- Cyclic role assignment (person1 → person2 → person3 → person1)
- Consistent role naming across messages

### FR-CA-004: Topic Extraction
- Optional `topic` field for conversation topic
- Optional `setting` field for context description
- Both included in English prompts

## Context Structure

```json
{
  "messages": [
    {"role": "person1", "content": "hey"},
    {"role": "person2", "content": "hey, what's up?"},
    {"role": "person1", "content": "nothing much, you?"}
  ],
  "topic": "casual chat",
  "setting": "friends texting"
}
```

## Prompt Generation (with Context)

**Russian (with length constraints)**
```
Чат:
person1: hey
person2: hey, what's up?
person1: nothing much, you?

Продолжи. 4 сообщений. {mention_instruction}

ДЛИНА СООБЩЕНИЙ: максимум {max_len} символов! В среднем ~{avg_len}.
Короткие фразы как выше. Без длинных предложений.

JSON: [{"role": "person1", "text": "короткое"}, ...]
```

**English**
```
Write 4 chat messages.

Topic: casual chat
Setting: friends texting
Previous messages:
person1: hey
person2: hey, what's up?
person1: nothing much, you?

Continue this conversation:
...
```

## Single Response Mode

For interactive sessions:
- `SingleResponseRequest` requires context
- Returns single `DialogMessage`
- Determines appropriate next speaker
- Maintains conversation flow

## CLI Usage

```bash
# Create context file
cat > context.json << 'EOF'
[
  {"role": "person1", "content": "hey"},
  {"role": "person2", "content": "what's up?"},
  {"role": "person1", "content": "hungry tbh"}
]
EOF

# Generate with context
dialog-gen generate -n "FoodBox" -d "delivery" -c context.json
```

## Code Reference (ast-grep)

### Classes
- `class DialogContext` - Context container with messages, topic, setting
- `class SingleResponseRequest` - Request for single response generation

### Key Functions
- `def _build_generation_prompt($$$) -> str` - Build prompt with context
- `async def generate_single_response(self, request: SingleResponseRequest) -> DialogMessage` - Generate single response

### Properties
- `DialogContext.messages` - List of previous messages [{role, content}, ...]
- `DialogContext.topic` - Optional conversation topic
- `DialogContext.setting` - Optional context description
- `GenerateRequest.context` - Optional DialogContext

## Verification Criteria

- [ ] Context messages appear in prompt
- [ ] Generated messages match context style
- [ ] Message length stays within observed limits
- [ ] Role assignment is consistent
- [ ] Single response mode works correctly

## Related

- [Dialog Generation](./feature-dialog-generation.md)
- [Generator Architecture](../architecture/generator.md)
