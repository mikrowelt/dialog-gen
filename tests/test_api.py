"""Tests for API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from dialog_gen.api import app
from dialog_gen.models import DialogMessage, GeneratedDialog


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_ok(self, client):
        """Health endpoint returns status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGenerateEndpoint:
    """Tests for /generate endpoint."""

    def test_generate_dialog_success(self, client):
        """Generate dialog returns generated messages."""
        mock_dialog = GeneratedDialog(
            messages=[
                DialogMessage(role="person1", content="Привет!"),
                DialogMessage(role="person2", content="Привет, как дела?")
            ],
            model_used="test-model",
            generation_params={"temperature": 0.8}
        )

        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.provider = "anthropic"
            mock_gen.generate_dialog = AsyncMock(return_value=mock_dialog)
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "num_turns": 4
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        assert data["model_used"] == "test-model"

    def test_generate_dialog_handles_error(self, client):
        """Generate dialog returns 500 on generation error."""
        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.provider = "anthropic"
            mock_gen.generate_dialog = AsyncMock(side_effect=Exception("Generation failed"))
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "subject": {"name": "FoodBox", "description": "food delivery"}
            })

        assert response.status_code == 500
        assert "Generation failed" in response.json()["detail"]

    def test_generate_dialog_handles_value_error(self, client):
        """Generate dialog returns 400 on ValueError (e.g., unknown provider)."""
        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.provider = "anthropic"
            mock_gen.generate_dialog = AsyncMock(side_effect=ValueError("Unknown provider"))
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "subject": {"name": "FoodBox", "description": "food delivery"}
            })

        assert response.status_code == 400
        assert "Unknown provider" in response.json()["detail"]

    def test_generate_dialog_with_brand_alias(self, client):
        """Generate dialog accepts brand as alias for subject."""
        mock_dialog = GeneratedDialog(
            messages=[DialogMessage(role="person1", content="Test")],
            model_used="test-model",
            generation_params={}
        )

        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.provider = "anthropic"
            mock_gen.generate_dialog = AsyncMock(return_value=mock_dialog)
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "brand": {"name": "FoodBox", "description": "food delivery"},
                "num_turns": 2
            })

        assert response.status_code == 200


class TestRespondEndpoint:
    """Tests for /respond endpoint."""

    def test_respond_success(self, client):
        """Respond endpoint returns single message."""
        mock_message = DialogMessage(
            role="person2",
            content="Хорошо, спасибо!",
            delay_hint=2.5
        )

        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.provider = "anthropic"
            mock_gen.generate_single_response = AsyncMock(return_value=mock_message)
            mock_gen_class.return_value = mock_gen

            response = client.post("/respond", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "context": {
                    "messages": [
                        {"role": "person1", "content": "Привет!"}
                    ]
                },
                "campaign": {}
            })

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "person2"
        assert data["content"] == "Хорошо, спасибо!"


class TestCompareEndpoint:
    """Tests for /compare endpoint."""

    def test_compare_models_success(self, client):
        """Compare returns results for each model."""
        mock_dialog = GeneratedDialog(
            messages=[DialogMessage(role="person1", content="Test")],
            model_used="model1",
            generation_params={}
        )

        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_dialog = AsyncMock(return_value=mock_dialog)
            mock_gen_class.return_value = mock_gen

            response = client.post("/compare", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "models": ["gpt-4o-mini", "claude-3-haiku"]
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_compare_handles_generation_error(self, client):
        """Compare handles generation errors gracefully."""
        with patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_dialog = AsyncMock(side_effect=Exception("Failed"))
            mock_gen_class.return_value = mock_gen

            response = client.post("/compare", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "models": ["gpt-4o-mini"]
            })

        assert response.status_code == 200
        data = response.json()
        assert "error" in data[0]["dialog"]["generation_params"]


class TestRequestValidation:
    """Tests for request validation."""

    def test_generate_requires_subject_or_brand(self, client):
        """Generate requires either subject or brand."""
        response = client.post("/generate", json={
            "num_turns": 4
        })

        assert response.status_code == 422

    def test_respond_requires_context(self, client):
        """Respond requires context."""
        response = client.post("/respond", json={
            "subject": {"name": "FoodBox", "description": "food delivery"},
            "campaign": {}
        })

        assert response.status_code == 422

    def test_compare_requires_models(self, client):
        """Compare requires models list."""
        response = client.post("/compare", json={
            "subject": {"name": "FoodBox", "description": "food delivery"}
        })

        assert response.status_code == 422
