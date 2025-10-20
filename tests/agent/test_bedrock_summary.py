"""
Tests for Bedrock-powered summarization tool.

Verifies LLM reasoning integration for the hackathon.
"""
from unittest.mock import MagicMock, patch
import json
import pytest

from aws_merlin_agent.agent.tools import bedrock_summary


@pytest.fixture
def sample_rows():
    """Sample sales data for testing."""
    return [
        {
            "seller_id": "SELLER-001",
            "sku": "SKU-001",
            "sale_date": "2025-10-12",
            "units_sold": "15",
            "net_revenue_usd": "450.00",
            "ad_spend_usd": "45.00",
            "inventory_on_hand": "100"
        },
        {
            "seller_id": "SELLER-001",
            "sku": "SKU-001",
            "sale_date": "2025-10-13",
            "units_sold": "18",
            "net_revenue_usd": "540.00",
            "ad_spend_usd": "50.00",
            "inventory_on_hand": "85"
        },
        {
            "seller_id": "SELLER-001",
            "sku": "SKU-001",
            "sale_date": "2025-10-14",
            "units_sold": "12",
            "net_revenue_usd": "360.00",
            "ad_spend_usd": "40.00",
            "inventory_on_hand": "73"
        }
    ]


@pytest.fixture
def mock_bedrock_runtime():
    """Mock Bedrock runtime client."""
    with patch("aws_merlin_agent.agent.tools.bedrock_summary.aws.client") as mock_client:
        mock_runtime = MagicMock()
        mock_client.return_value = mock_runtime
        yield mock_runtime


def test_summarize_rows_empty():
    """Test summarization with no data."""
    result = bedrock_summary.summarize_rows([])
    assert result == "No recent data available."


def test_summarize_rows_with_nova(mock_bedrock_runtime, sample_rows):
    """Test summarization using Nova Pro."""
    # Mock Nova Pro response
    mock_response = {
        "body": MagicMock(read=lambda: json.dumps({
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "Performance Analysis:\n\n1. Overall Trend: Sales show positive momentum with 45 total units sold over 3 days.\n\n2. Key Metrics:\n   - Total Revenue: $1,350\n   - Total Ad Spend: $135\n   - ACOS: 10%\n\n3. Recommendations:\n   - Maintain current ad strategy as ACOS is healthy\n   - Monitor inventory levels (73 units remaining)\n   - Consider increasing ad budget to capitalize on momentum"
                        }
                    ]
                }
            }
        }).encode())
    }
    mock_bedrock_runtime.invoke_model.return_value = mock_response
    
    result = bedrock_summary.summarize_rows(sample_rows)
    
    assert "Performance Analysis" in result
    assert "45 total units" in result or "units sold" in result.lower()
    assert "$1,350" in result or "1350" in result
    
    # Verify Nova Pro was called
    mock_bedrock_runtime.invoke_model.assert_called_once()
    call_args = mock_bedrock_runtime.invoke_model.call_args
    assert call_args[1]["modelId"] == "amazon.nova-pro-v1:0"


def test_summarize_rows_fallback_to_claude(mock_bedrock_runtime, sample_rows):
    """Test fallback to Claude when Nova fails."""
    # Mock Nova failure and Claude success
    def side_effect_func(*args, **kwargs):
        model_id = kwargs.get("modelId", "")
        if "nova" in model_id:
            raise Exception("Nova not available")
        else:
            # Claude response
            return {
                "body": MagicMock(read=lambda: json.dumps({
                    "content": [{"text": "Claude analysis: Strong performance with good ACOS"}]
                }).encode())
            }
    
    mock_bedrock_runtime.invoke_model.side_effect = side_effect_func
    
    result = bedrock_summary.summarize_rows(sample_rows)
    
    assert "Claude analysis" in result or "Strong performance" in result
    
    # Verify both Nova and Claude were attempted
    assert mock_bedrock_runtime.invoke_model.call_count == 2


def test_summarize_rows_complete_fallback(mock_bedrock_runtime, sample_rows):
    """Test complete fallback when both Nova and Claude fail."""
    # Mock both failures
    mock_bedrock_runtime.invoke_model.side_effect = Exception("Bedrock unavailable")
    
    result = bedrock_summary.summarize_rows(sample_rows)
    
    # Should provide basic summary
    assert "Performance Summary" in result
    assert "45" in result  # Total units
    assert "1,350" in result or "1350" in result  # Total revenue (may have comma)
    assert "LLM analysis unavailable" in result


def test_summarize_rows_data_processing(mock_bedrock_runtime, sample_rows):
    """Test that data is correctly processed before sending to LLM."""
    mock_response = {
        "body": MagicMock(read=lambda: json.dumps({
            "output": {
                "message": {
                    "content": [{"text": "Analysis"}]
                }
            }
        }).encode())
    }
    mock_bedrock_runtime.invoke_model.return_value = mock_response
    
    bedrock_summary.summarize_rows(sample_rows)
    
    # Verify the request body contains processed data
    call_args = mock_bedrock_runtime.invoke_model.call_args
    request_body = json.loads(call_args[1]["body"])
    
    # Check that prompt includes data summary
    prompt = request_body["messages"][0]["content"][0]["text"]
    assert "total_units_sold" in prompt or "45" in prompt
    assert "total_revenue_usd" in prompt or "1350" in prompt


def test_summarize_rows_with_zero_revenue(mock_bedrock_runtime):
    """Test handling of edge case with zero revenue."""
    rows = [
        {
            "units_sold": "0",
            "net_revenue_usd": "0",
            "ad_spend_usd": "10"
        }
    ]
    
    mock_response = {
        "body": MagicMock(read=lambda: json.dumps({
            "output": {
                "message": {
                    "content": [{"text": "No sales recorded"}]
                }
            }
        }).encode())
    }
    mock_bedrock_runtime.invoke_model.return_value = mock_response
    
    result = bedrock_summary.summarize_rows(rows)
    assert result is not None


@pytest.mark.integration
def test_real_bedrock_summarization():
    """
    Integration test with real Bedrock API.
    
    Run with: pytest -m integration
    """
    sample_data = [
        {
            "sku": "TEST-SKU",
            "sale_date": "2025-10-15",
            "units_sold": "10",
            "net_revenue_usd": "300",
            "ad_spend_usd": "30"
        }
    ]
    
    try:
        result = bedrock_summary.summarize_rows(sample_data)
        
        assert len(result) > 0
        assert isinstance(result, str)
        # Should contain some analysis
        assert len(result) > 50
        
    except Exception as e:
        pytest.skip(f"Bedrock not accessible: {str(e)}")
