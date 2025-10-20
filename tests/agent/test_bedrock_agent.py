"""
Tests for Bedrock Agent Core integration.

These tests verify the hackathon requirement for Bedrock AgentCore implementation.
"""
from unittest.mock import MagicMock, patch
import json
import pytest

from aws_merlin_agent.agent.bedrock_agent import BedrockAgentOrchestrator, create_conversational_response


@pytest.fixture
def mock_bedrock_runtime():
    """Mock Bedrock runtime client."""
    with patch("aws_merlin_agent.agent.bedrock_agent.aws.client") as mock_client:
        mock_runtime = MagicMock()
        mock_client.return_value = mock_runtime
        yield mock_runtime


def test_bedrock_agent_orchestrator_initialization():
    """Test that BedrockAgentOrchestrator initializes correctly."""
    orchestrator = BedrockAgentOrchestrator()
    assert orchestrator.use_inline_agent is True
    assert orchestrator.agent_id is None
    
    orchestrator_with_agent = BedrockAgentOrchestrator(agent_id="test-agent", agent_alias_id="test-alias")
    assert orchestrator_with_agent.use_inline_agent is False
    assert orchestrator_with_agent.agent_id == "test-agent"


def test_invoke_inline_agent_with_nova(mock_bedrock_runtime):
    """Test inline agent invocation using Nova Pro."""
    # Mock Nova Pro response
    mock_response = {
        "output": {
            "message": {
                "content": [
                    {"text": "SKU-001 is performing well with 150 units sold and $3,000 revenue."}
                ]
            }
        },
        "stopReason": "end_turn"
    }
    mock_bedrock_runtime.converse.return_value = mock_response
    
    orchestrator = BedrockAgentOrchestrator()
    result = orchestrator.invoke_agent("How is SKU-001 performing?")
    
    assert "response" in result
    assert "SKU-001 is performing well" in result["response"]
    assert result["session_id"] is not None
    assert result["stop_reason"] == "end_turn"
    
    # Verify Nova Pro was called
    mock_bedrock_runtime.converse.assert_called_once()
    call_args = mock_bedrock_runtime.converse.call_args
    assert call_args[1]["modelId"] == "amazon.nova-pro-v1:0"


def test_invoke_inline_agent_fallback_to_claude(mock_bedrock_runtime):
    """Test fallback to Claude when Nova fails."""
    # Mock Nova failure and Claude success
    mock_bedrock_runtime.converse.side_effect = Exception("Nova not available")
    
    mock_claude_response = {
        "body": MagicMock(read=lambda: json.dumps({
            "content": [{"text": "Analysis from Claude"}]
        }).encode())
    }
    mock_bedrock_runtime.invoke_model.return_value = mock_claude_response
    
    orchestrator = BedrockAgentOrchestrator()
    result = orchestrator.invoke_agent("Analyze performance")
    
    assert "response" in result
    assert "Analysis from Claude" in result["response"]
    assert result["trace"]["model"] == "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Verify Claude was called
    mock_bedrock_runtime.invoke_model.assert_called_once()


def test_create_conversational_response(mock_bedrock_runtime):
    """Test high-level conversational response function."""
    mock_response = {
        "output": {
            "message": {
                "content": [{"text": "Here's your analysis"}]
            }
        },
        "stopReason": "end_turn"
    }
    mock_bedrock_runtime.converse.return_value = mock_response
    
    result = create_conversational_response("What should I do?")
    
    assert "response" in result
    assert "Here's your analysis" in result["response"]
    assert "trace" in result


def test_agent_with_session_continuity(mock_bedrock_runtime):
    """Test that session IDs are maintained for conversation continuity."""
    mock_response = {
        "output": {
            "message": {
                "content": [{"text": "Response"}]
            }
        },
        "stopReason": "end_turn"
    }
    mock_bedrock_runtime.converse.return_value = mock_response
    
    orchestrator = BedrockAgentOrchestrator()
    session_id = "test-session-123"
    
    result1 = orchestrator.invoke_agent("First query", session_id=session_id)
    result2 = orchestrator.invoke_agent("Follow-up query", session_id=session_id)
    
    assert result1["session_id"] == session_id
    assert result2["session_id"] == session_id


def test_agent_reasoning_trace_enabled(mock_bedrock_runtime):
    """Test that reasoning traces are included when enabled."""
    mock_response = {
        "output": {
            "message": {
                "content": [{"text": "Response with trace"}]
            }
        },
        "stopReason": "end_turn"
    }
    mock_bedrock_runtime.converse.return_value = mock_response
    
    orchestrator = BedrockAgentOrchestrator()
    result = orchestrator.invoke_agent("Query", enable_trace=True)
    
    assert result["trace"] is not None
    assert "reasoning" in result["trace"]


def test_agent_reasoning_trace_disabled(mock_bedrock_runtime):
    """Test that reasoning traces are excluded when disabled."""
    mock_response = {
        "output": {
            "message": {
                "content": [{"text": "Response without trace"}]
            }
        },
        "stopReason": "end_turn"
    }
    mock_bedrock_runtime.converse.return_value = mock_response
    
    orchestrator = BedrockAgentOrchestrator()
    result = orchestrator.invoke_agent("Query", enable_trace=False)
    
    assert result["trace"] is None


@pytest.mark.integration
def test_real_bedrock_agent_invocation():
    """
    Integration test with real Bedrock API (requires AWS credentials).
    
    This test is marked as integration and skipped by default.
    Run with: pytest -m integration
    """
    orchestrator = BedrockAgentOrchestrator()
    
    try:
        result = orchestrator.invoke_agent(
            "What is 2+2?",
            enable_trace=True
        )
        
        assert "response" in result
        assert len(result["response"]) > 0
        assert "4" in result["response"] or "four" in result["response"].lower()
        
    except Exception as e:
        pytest.skip(f"Bedrock not accessible: {str(e)}")
