from unittest.mock import MagicMock, patch
import pytest
from backend.app.agent.nodes.email_classifier_node import EmailClassifierNode, EmailCategory
from backend.app.agent.nodes.email_judge_node import EmailJudgeNode, EmailJudgeDecision


def test_email_classifier_node_success():
    # Arrange
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    mock_structured_llm.invoke.return_value = EmailCategory(
        category="promotions",
        reason="Has promo code BOGO"
    )

    node = EmailClassifierNode(mock_llm)
    state = {"subject": "Promo", "body": "BOGO code"}

    # Act
    res = node.process(state)

    # Assert
    assert res == {
        "category": "promotions",
        "reason": "Has promo code BOGO"
    }
    mock_llm.with_structured_output.assert_called_once_with(EmailCategory)
    mock_structured_llm.invoke.assert_called_once()


def test_email_classifier_node_error():
    # Arrange
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    mock_structured_llm.invoke.side_effect = Exception("LLM connection timed out")

    node = EmailClassifierNode(mock_llm)
    state = {"subject": "Promo", "body": "BOGO code"}

    # Act
    res = node.process(state)

    # Assert
    assert res["category"] == "Unknown"
    assert "LLM connection timed out" in res["reason"]


@patch("backend.app.agent.nodes.email_judge_node._create_judge_llm")
def test_email_judge_node_accept(mock_create_llm):
    # Arrange
    mock_base_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_base_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_base_llm

    mock_structured_llm.invoke.return_value = EmailJudgeDecision(
        accepted=True,
        reason="It is indeed promotions"
    )

    node = EmailJudgeNode()
    state = {"subject": "Promo", "body": "BOGO code", "category": "promotions"}

    # Act
    res = node.process(state)

    # Assert
    assert res == {
        "JudgeVerted": "accept",
        "JudgeReasoning": "It is indeed promotions"
    }


@patch("backend.app.agent.nodes.email_judge_node._create_judge_llm")
def test_email_judge_node_reject(mock_create_llm):
    # Arrange
    mock_base_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_base_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_base_llm

    mock_structured_llm.invoke.return_value = EmailJudgeDecision(
        accepted=False,
        reason="Doesn't look like promotions"
    )

    node = EmailJudgeNode()
    state = {"subject": "Promo", "body": "BOGO code", "category": "promotions"}

    # Act
    res = node.process(state)

    # Assert
    assert res == {
        "JudgeVerted": "reject",
        "JudgeReasoning": "Doesn't look like promotions"
    }


@patch("backend.app.agent.nodes.email_judge_node._create_judge_llm")
def test_email_judge_node_error(mock_create_llm):
    # Arrange
    mock_base_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_base_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_base_llm

    mock_structured_llm.invoke.side_effect = Exception("Azure OpenAI API error")

    node = EmailJudgeNode()
    state = {"subject": "Promo", "body": "BOGO code", "category": "promotions"}

    # Act
    res = node.process(state)

    # Assert
    assert res["JudgeVerted"] == "reject"
    assert "Azure OpenAI API error" in res["JudgeReasoning"]
