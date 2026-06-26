import pytest
from unittest.mock import MagicMock, patch
from backend.app.agent.builder import GraphBuilder
from backend.app.agent.nodes.email_classifier_node import EmailCategory
from backend.app.agent.nodes.email_judge_node import EmailJudgeDecision


@pytest.mark.asyncio
@patch("backend.app.agent.nodes.email_judge_node._create_judge_llm")
async def test_graph_builder_and_execution(mock_create_judge_llm):
    # Arrange: Mock the classifier LLM
    mock_classifier_llm = MagicMock()
    mock_classifier_structured = MagicMock()
    mock_classifier_llm.with_structured_output.return_value = mock_classifier_structured
    mock_classifier_structured.invoke.return_value = EmailCategory(
        category="promotions",
        reason="It contains promotional links."
    )

    # Arrange: Mock the judge LLM
    mock_judge_llm = MagicMock()
    mock_judge_structured = MagicMock()
    mock_judge_llm.with_structured_output.return_value = mock_judge_structured
    mock_create_judge_llm.return_value = mock_judge_llm
    mock_judge_structured.invoke.return_value = EmailJudgeDecision(
        accepted=True,
        reason="The promotions category fits perfectly."
    )

    # Act: Build the graph
    builder = GraphBuilder(mock_classifier_llm)
    graph = await builder.setup_graph("basic_chatbot")
    assert graph is not None

    # Run the graph
    initial_state = {
        "subject": "Discount coupon inside!",
        "body": "Get 20% off using coupon code SAVE20.",
        "category": None,
        "reason": None,
        "JudgeVerted": None,
        "JudgeReasoning": None,
    }

    result = await graph.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": "test-thread"}}
    )

    # Assert results updated in state
    assert result["category"] == "promotions"
    assert result["reason"] == "It contains promotional links."
    assert result["JudgeVerted"] == "accept"
    assert result["JudgeReasoning"] == "The promotions category fits perfectly."
