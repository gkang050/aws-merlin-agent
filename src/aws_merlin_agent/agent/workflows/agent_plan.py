from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import pandas as pd

from aws_merlin_agent.agent.tools import bedrock_summary, metrics_query
from aws_merlin_agent.agent.bedrock_agent import BedrockAgentOrchestrator
from aws_merlin_agent.features.engineering import build_feature_frame
from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.models.inference.demand_forecast_client import DemandForecastClient
from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


class MerlinAgentWorkflow:
    """
    Composable workflow using Bedrock Agent Core for intelligent orchestration.
    
    This implements the hackathon requirement for autonomous AI agent capabilities
    with reasoning LLMs and tool integration.
    """

    def __init__(self) -> None:
        self.settings = EnvironmentSettings.load()
        self.forecast_client = DemandForecastClient()
        
        # Initialize Bedrock Agent orchestrator
        agent_id = os.getenv("BEDROCK_AGENT_ID")
        agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID")
        self.bedrock_agent = BedrockAgentOrchestrator(agent_id, agent_alias_id)

    def _fetch_recent_rows(self, sku: str, limit: int = 7) -> List[Dict[str, str]]:
        sql = f"""
        SELECT seller_id, sku, sale_date, units_sold, net_revenue_usd, ad_spend_usd, inventory_on_hand
        FROM sales_fact
        WHERE sku = '{sku}'
        ORDER BY sale_date DESC
        LIMIT {limit};
        """
        rows = metrics_query.run_kpi_query(sql, max_results=limit + 2)
        for row in rows:
            for key in ("units_sold", "net_revenue_usd", "ad_spend_usd", "inventory_on_hand"):
                if key in row and row[key] is not None:
                    try:
                        row[key] = float(row[key])
                    except (TypeError, ValueError):
                        row[key] = 0.0
        rows.sort(key=lambda r: r.get("sale_date"))
        logger.info("Collected %d rows for sku=%s", len(rows), sku)
        return rows

    def summarize_performance(self, sku: str) -> Dict[str, object]:
        """
        Generate intelligent performance summary using Bedrock LLM reasoning.
        
        This demonstrates the AI agent's ability to analyze data and provide insights.
        """
        rows = self._fetch_recent_rows(sku)
        narrative = bedrock_summary.summarize_rows(rows)
        return {"narrative": narrative, "rows": rows}
    
    def conversational_query(self, user_query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle natural language queries using Bedrock Agent orchestration.
        
        This is the main entry point for conversational AI interactions,
        demonstrating autonomous agent capabilities with reasoning LLMs.
        
        Args:
            user_query: Natural language question from the user
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dict containing agent response, reasoning trace, and any tool outputs
        """
        logger.info("Processing conversational query: %s", user_query)
        
        # Use Bedrock Agent to orchestrate the response
        agent_response = self.bedrock_agent.invoke_agent(
            prompt=user_query,
            session_id=session_id,
            enable_trace=True
        )
        
        # Check if agent needs to execute tools
        if "action_required" in agent_response:
            # Execute the requested action and return results
            action = agent_response["action_required"]
            if action == "query_metrics":
                # Agent wants to query metrics
                sku = agent_response.get("parameters", {}).get("sku", "SKU-001")
                rows = self._fetch_recent_rows(sku)
                agent_response["tool_output"] = rows
            elif action == "forecast_demand":
                # Agent wants a forecast
                sku = agent_response.get("parameters", {}).get("sku", "SKU-001")
                forecast = self.forecast(sku=sku)
                agent_response["tool_output"] = forecast
        
        return agent_response

    def prepare_forecast_payload(self, sku: str, window: int = 7) -> Dict[str, List[Dict[str, float]]]:
        rows = self._fetch_recent_rows(sku, limit=window)
        if not rows:
            return {"instances": []}

        frame = pd.DataFrame(rows)
        frame = frame.rename(
            columns={
                "sale_date": "date",
                "net_revenue_usd": "net_revenue",
                "ad_spend_usd": "ad_spend",
            }
        )
        engineered = build_feature_frame(frame.dropna(subset=["units_sold"]))
        engineered["lag_days"] = range(len(engineered))
        numeric_features = engineered.select_dtypes(include=["number"]).copy()
        feature_frame = numeric_features.drop(columns=["units_sold"], errors="ignore")
        instances = feature_frame.to_dict(orient="records")
        return {"instances": instances}

    def forecast(
        self,
        feature_payload: Optional[Dict[str, List[Dict[str, float]]]] = None,
        sku: Optional[str] = None,
    ) -> Dict[str, float]:
        if feature_payload is None:
            if sku is None:
                raise ValueError("SKU must be provided when feature payload is absent")
            feature_payload = self.prepare_forecast_payload(sku)
        if not feature_payload.get("instances"):
            logger.warning("No feature instances available for forecast")
            return {"predictions": []}
        logger.info("Requesting forecast")
        return self.forecast_client.predict(feature_payload)


def lambda_handler(event, _context):
    """
    Entry point compatible with AWS Lambda / EventBridge that kicks off the agent workflow.

    Event schema mirrors EventBridge detail with `sku` and `forecast_payload`.
    """
    detail = event.get("detail", {}) or {}
    sku = detail.get("sku", "SKU-001")
    payload = detail.get("forecast_payload")

    workflow = MerlinAgentWorkflow()
    summary = workflow.summarize_performance(sku)
    forecast = workflow.forecast(payload, sku=sku)

    logger.info("Workflow complete for sku=%s", sku)
    return {"summary": summary, "forecast": forecast}
