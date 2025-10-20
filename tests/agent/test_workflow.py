import pytest

from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow
from aws_merlin_agent.agent.tools import metrics_query


@pytest.fixture
def sample_rows():
    return [
        {
            "seller_id": "seller-123",
            "sku": "SKU-001",
            "sale_date": "2024-02-01",
            "units_sold": "10",
            "net_revenue_usd": "200",
            "ad_spend_usd": "20",
            "inventory_on_hand": "50",
        },
        {
            "seller_id": "seller-123",
            "sku": "SKU-001",
            "sale_date": "2024-02-02",
            "units_sold": "12",
            "net_revenue_usd": "240",
            "ad_spend_usd": "24",
            "inventory_on_hand": "48",
        },
    ]


def test_prepare_forecast_payload(monkeypatch, sample_rows, dummy_settings):
    monkeypatch.setattr(metrics_query, "run_kpi_query", lambda sql, max_results: sample_rows)
    workflow = MerlinAgentWorkflow()
    payload = workflow.prepare_forecast_payload("SKU-001")
    assert "instances" in payload
    assert len(payload["instances"]) == 2
    first_instance = payload["instances"][0]
    assert "net_revenue" in first_instance
    assert "lag_days" in first_instance


def test_lambda_handler_generates_forecast(monkeypatch, sample_rows, dummy_settings):
    monkeypatch.setattr(metrics_query, "run_kpi_query", lambda sql, max_results: sample_rows)

    class StubForecastClient:
        def predict(self, payload):
            self.payload = payload
            return {"predictions": [42.0]}

    workflow = MerlinAgentWorkflow()
    workflow.forecast_client = StubForecastClient()

    result = workflow.forecast(sku="SKU-001")
    assert result["predictions"][0] == 42.0
