from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "email-classifier-api"}


@patch("backend.app.api.routes.classify.build_llm_with_fallbacks")
@patch("backend.app.api.routes.classify.GraphBuilder")
def test_classify_email_success(mock_builder_cls, mock_build_llm):
    # Arrange
    mock_llm = MagicMock()
    mock_build_llm.return_value = mock_llm

    mock_builder = MagicMock()
    mock_builder.setup_graph = AsyncMock()
    mock_builder_cls.return_value = mock_builder

    mock_graph = MagicMock()
    mock_builder.setup_graph.return_value = mock_graph

    mock_graph.ainvoke = AsyncMock()
    mock_graph.ainvoke.return_value = {
        "subject": "Discount offer",
        "body": "Special sale!",
        "category": "promotions",
        "reason": "Discount offer body",
        "JudgeVerted": "accept",
        "JudgeReasoning": "Promotions classification is correct"
    }

    # Act
    payload = {
        "subject": "Discount offer",
        "body": "Special sale!",
        "provider": "openai",
        "selected_llm": "gpt-4.1-mini",
        "thread_id": "test-thread"
    }
    response = client.post("/api/classify", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "promotions"
    assert data["reason"] == "Discount offer body"
    assert data["JudgeVerted"] == "accept"
    assert data["JudgeReasoning"] == "Promotions classification is correct"

    mock_build_llm.assert_called_once_with("openai", "gpt-4.1-mini")
    mock_builder_cls.assert_called_once_with(mock_llm)
    mock_builder.setup_graph.assert_called_once_with("basic_chatbot")


def test_classify_email_unsupported_provider():
    # Act
    payload = {
        "subject": "Discount offer",
        "body": "Special sale!",
        "provider": "invalid-provider",
        "selected_llm": None,
        "thread_id": "test-thread"
    }
    response = client.post("/api/classify", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Unsupported provider" in response.json()["detail"]


@patch("backend.app.api.routes.classify.build_llm_with_fallbacks")
def test_classify_email_llm_build_error(mock_build_llm):
    # Arrange
    mock_build_llm.side_effect = ValueError("No LLM providers available")

    # Act
    payload = {
        "subject": "Discount offer",
        "body": "Special sale!",
        "provider": "openai",
        "selected_llm": None,
        "thread_id": "test-thread"
    }
    response = client.post("/api/classify", json=payload)

    # Assert
    assert response.status_code == 400
    assert "No LLM providers available" in response.json()["detail"]


@patch("backend.app.api.routes.classify.build_llm_with_fallbacks")
@patch("backend.app.api.routes.classify.GraphBuilder")
def test_classify_email_unexpected_error(mock_builder_cls, mock_build_llm):
    # Arrange
    mock_llm = MagicMock()
    mock_build_llm.return_value = mock_llm

    mock_builder = MagicMock()
    mock_builder.setup_graph = AsyncMock()
    mock_builder_cls.return_value = mock_builder

    mock_graph = MagicMock()
    mock_builder.setup_graph.return_value = mock_graph

    mock_graph.ainvoke = AsyncMock()
    mock_graph.ainvoke.side_effect = Exception("Unexpected graph error")

    # Act
    payload = {
        "subject": "Discount offer",
        "body": "Special sale!",
        "provider": "openai",
        "selected_llm": None,
        "thread_id": "test-thread"
    }
    response = client.post("/api/classify", json=payload)

    # Assert
    assert response.status_code == 500
    assert "Email classification failed: Unexpected graph error" in response.json()["detail"]
