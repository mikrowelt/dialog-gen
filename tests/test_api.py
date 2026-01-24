"""Tests for API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from dialog_gen.api import app
from dialog_gen.models import ModelInfo, DialogMessage, GeneratedDialog


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


class TestModelsEndpoint:
    """Tests for /models endpoint."""

    def test_list_models_returns_models(self, client):
        """List models returns available models."""
        mock_models = [
            ModelInfo(name="hermes3:8b", size="4.9GB", modified_at="2024-01-01"),
            ModelInfo(name="dolphin3:latest", size="4.7GB", modified_at="2024-01-02")
        ]

        with patch('dialog_gen.api.ollama.list_models', new_callable=AsyncMock) as mock:
            mock.return_value = mock_models
            response = client.get("/models")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "hermes3:8b"

    def test_list_models_handles_ollama_unavailable(self, client):
        """List models returns 503 when Ollama is unavailable."""
        with patch('dialog_gen.api.ollama.list_models', new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("Connection refused")
            response = client.get("/models")

        assert response.status_code == 503
        assert "Ollama not available" in response.json()["detail"]


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

        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
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

    def test_generate_dialog_model_not_found(self, client):
        """Generate dialog returns 400 for missing Ollama model."""
        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = False
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "model": "nonexistent-model"
            })

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_generate_dialog_handles_error(self, client):
        """Generate dialog returns 500 on generation error."""
        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
            mock_gen.generate_dialog = AsyncMock(side_effect=Exception("Generation failed"))
            mock_gen_class.return_value = mock_gen

            response = client.post("/generate", json={
                "subject": {"name": "FoodBox", "description": "food delivery"}
            })

        assert response.status_code == 500
        assert "Generation failed" in response.json()["detail"]

    def test_generate_dialog_with_brand_alias(self, client):
        """Generate dialog accepts brand as alias for subject."""
        mock_dialog = GeneratedDialog(
            messages=[DialogMessage(role="person1", content="Test")],
            model_used="test-model",
            generation_params={}
        )

        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
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

        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
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

    def test_respond_model_not_found(self, client):
        """Respond returns 400 for missing model."""
        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = False
            mock_gen = MagicMock()
            mock_gen.provider = "ollama"
            mock_gen_class.return_value = mock_gen

            response = client.post("/respond", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "context": {"messages": []},
                "campaign": {},
                "model": "nonexistent"
            })

        assert response.status_code == 400


class TestCompareEndpoint:
    """Tests for /compare endpoint."""

    def test_compare_models_success(self, client):
        """Compare returns results for each model."""
        mock_dialog = GeneratedDialog(
            messages=[DialogMessage(role="person1", content="Test")],
            model_used="model1",
            generation_params={}
        )

        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.generate_dialog = AsyncMock(return_value=mock_dialog)
            mock_gen_class.return_value = mock_gen

            response = client.post("/compare", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "models": ["model1", "model2"]
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_compare_handles_missing_model(self, client):
        """Compare handles missing models gracefully."""
        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = False

            response = client.post("/compare", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "models": ["nonexistent"]
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["dialog"]["generation_params"]["error"] == "Model not found"

    def test_compare_handles_generation_error(self, client):
        """Compare handles generation errors gracefully."""
        with patch('dialog_gen.api.ollama.model_exists', new_callable=AsyncMock) as mock_exists, \
             patch('dialog_gen.api.DialogGenerator') as mock_gen_class:
            mock_exists.return_value = True
            mock_gen = MagicMock()
            mock_gen.generate_dialog = AsyncMock(side_effect=Exception("Failed"))
            mock_gen_class.return_value = mock_gen

            response = client.post("/compare", json={
                "subject": {"name": "FoodBox", "description": "food delivery"},
                "models": ["model1"]
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
