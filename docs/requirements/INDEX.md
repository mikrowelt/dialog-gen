# Requirements Documentation

This section documents the functional requirements and feature specifications for Dialog-Gen.

## Feature List

| Feature | Status | Description |
|---------|--------|-------------|
| [Dialog Generation](./feature-dialog-generation.md) | Production | Core multi-turn dialog generation |
| [Subject Types](./feature-subject-types.md) | Production | 6 subject types with localized prompts |
| [Multi-Language](./feature-multi-language.md) | Production | Russian and English support |
| [Context Awareness](./feature-context-awareness.md) | Production | Continue existing conversations |
| [Configuration](./feature-configuration.md) | Production | File + environment config system |
| [LLM Providers](./feature-providers.md) | Production | Ollama, OpenAI, Anthropic support |

## User Personas

### Marketing Team
- Generate brand mention dialogs for social media campaigns
- Compare output across different models
- Batch generation via API

### Content Creator
- Create realistic conversation snippets
- Inject topic discussions naturally
- Multi-language content

### Developer
- Integrate via REST API
- Automate dialog generation
- Custom model selection

## Core User Stories

1. **As a marketer**, I want to generate natural-sounding dialogs that mention my brand so that promotional content feels authentic.

2. **As a content creator**, I want to inject discussion topics into conversations so that information spreads naturally.

3. **As a developer**, I want to call a REST API with subject details and receive generated dialogs so that I can automate content creation.

4. **As a user**, I want to continue an existing conversation so that generated content flows naturally from real context.
