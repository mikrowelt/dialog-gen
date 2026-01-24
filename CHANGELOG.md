# Changelog

All notable changes to dialog-gen are documented in this file.

## [Unreleased]

### Added
- **Cloud model support** using Anthropic API instead of local Ollama
- **Registry authentication** for GitHub Container Registry
- **Dockerfile** and GitHub Actions deploy workflow
- **REST API** for dialog generation
- **CLI interface** for local testing
- **Configurable settings** via environment variables
- **Multi-provider support** architecture
- **utils module** with shared `detect_provider()` function
- **Tests for generate_dialog** async method with mocked LLM calls
- **CLAUDE.md** project-specific instructions for AI assistants

### Changed
- Switched from Ollama (local) to Anthropic (cloud) for AI inference
- Updated deployment workflow for Docker-based deployment
- **Refactored provider detection** - consolidated duplicate `detect_provider` implementations from cli.py, cloud_client.py, and generator.py into shared `utils.py` module
- **CLI compare command** now supports cloud providers (OpenAI, Anthropic), not just local Ollama models

### Fixed
- Model validation for cloud providers

## [2026-01-19]

### Added
- Initial release
- Dialog generation service using AI
- Support for multiple AI providers (Ollama, Anthropic)
- REST API endpoints:
  - `POST /generate` - Generate dialog from parameters
  - `GET /health` - Health check
- Configurable via environment variables:
  - `MODEL_PROVIDER` - AI provider (ollama/anthropic)
  - `ANTHROPIC_API_KEY` - API key for Anthropic
  - `OLLAMA_BASE_URL` - URL for local Ollama
- Docker containerization

---

For full commit history, see [GitHub](https://github.com/mikrowelt/dialog-gen/commits/main).
