# Feature: Dialog Generation

## Overview

Core capability to generate multi-turn, multi-person conversations with natural subject mentions.

## Functional Requirements

### FR-DG-001: Multi-Turn Generation
- System MUST generate 1-20 messages per request
- Default: 4 messages
- Each message includes role, content, and delay hint

### FR-DG-002: Multi-Person Support
- System MUST support person1, person2, person3+ roles
- Role assignment determined by conversation flow
- Cyclic role assignment for continuation

### FR-DG-003: Natural Subject Mention
- Generated dialog MUST mention subject naturally
- Mention style adapts to subject type
- No "advertisement-like" language

### FR-DG-004: Typing Delay Hints
- Each message includes realistic typing delay
- Formula: `word_count * 1.5 * random(0.8-1.2)`
- Maximum: 30 seconds

### FR-DG-005: Output Format
- Returns structured `GeneratedDialog` object
- Includes: messages, model_used, generation_params
- generation_params contains timing metrics

## Input Specification

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| subject | Subject | Yes | - | Subject to mention |
| campaign | Campaign | No | defaults | Style settings |
| context | DialogContext | No | null | Previous messages |
| num_turns | int | No | 4 | Messages to generate (1-20) |
| model | string | No | settings | Model override |
| temperature | float | No | 0.8 | Creativity (0-2) |
| language | string | No | "ru" | Language code |

## Output Specification

```json
{
  "messages": [
    {
      "role": "person1",
      "content": "message text",
      "delay_hint": 2.5
    }
  ],
  "model_used": "hermes3:8b",
  "generation_params": {
    "provider": "ollama",
    "temperature": 0.8,
    "generation_time_ms": 1500,
    "raw_response_length": 450
  }
}
```

## Code Reference (ast-grep)

### Classes
- `class DialogGenerator` - Core generation engine
- `class GenerateRequest` - Request model for generation
- `class GeneratedDialog` - Output model with messages and metadata
- `class DialogMessage` - Single message with role, content, delay_hint

### Key Functions
- `async def generate_dialog(self, request: GenerateRequest) -> GeneratedDialog` - Main generation entry point
- `def _build_system_prompt(self, subject, campaign, language) -> str` - Build system prompt
- `def _build_generation_prompt($$$) -> str` - Build user prompt
- `def _parse_dialog(self, raw_text: str) -> list[DialogMessage]` - Parse LLM output
- `def _calculate_delay(self, message: str) -> float` - Calculate typing delay

### Properties
- `DialogMessage.role` - Speaker identifier (person1, person2, etc.)
- `DialogMessage.content` - Message text
- `DialogMessage.delay_hint` - Typing delay in seconds
- `GeneratedDialog.messages` - List of DialogMessage
- `GeneratedDialog.model_used` - Model that generated the dialog
- `GeneratedDialog.generation_params` - Timing and provider info

## Verification Criteria

- [ ] 1-20 messages can be generated
- [ ] Multiple speakers appear in output
- [ ] Subject is mentioned naturally
- [ ] Delay hints are present and reasonable (0-30s)
- [ ] Generation completes within timeout

## Related

- [Subject Types](./feature-subject-types.md)
- [Context Awareness](./feature-context-awareness.md)
- [Generator Architecture](../architecture/generator.md)
