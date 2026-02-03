# Changelog

All notable changes to dialog-gen are documented in this file.

## [Unreleased]

### Changed

- **Return full LLM context in generation response** — `generation_params` dict now includes `system_prompt`, `generation_prompt`, and `raw_response` alongside existing fields (provider, temperature, timing, raw_response_length). Enables upstream services to persist and display the full LLM context for debugging.
