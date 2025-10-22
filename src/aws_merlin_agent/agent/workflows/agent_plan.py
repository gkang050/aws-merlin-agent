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
        # Check if running in demo/mock mode (no AWS credentials)
        inference_mode = os.getenv("MERLIN_INFERENCE_MODE", "local")
        
        if inference_mode == "local" or not os.getenv("AWS_ACCESS_KEY_ID"):
            # Return mock data for demo
            logger.info("Running in mock mode - returning sample data")
            return self._get_mock_data(sku, limit)
        
        # Real AWS mode
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
    
    def _get_mock_data(self, sku: str, limit: int = 7) -> List[Dict[str, str]]:
        """Generate mock data for demo mode."""
        import random
        from datetime import datetime, timedelta
        
        mock_rows = []
        base_date = datetime.now() - timedelta(days=limit)
        
        for i in range(limit):
            date = base_date + timedelta(days=i)
            units = random.randint(10, 25)
            revenue = units * random.uniform(25, 35)
            ad_spend = revenue * random.uniform(0.08, 0.12)
            
            mock_rows.append({
                "seller_id": "DEMO-SELLER",
                "sku": sku,
                "sale_date": date.strftime("%Y-%m-%d"),
                "units_sold": float(units),
                "net_revenue_usd": round(revenue, 2),
                "ad_spend_usd": round(ad_spend, 2),
                "inventory_on_hand": float(random.randint(50, 150))
            })
        
        return mock_rows

    def summarize_performance(self, sku: str) -> Dict[str, object]:
        """
        Generate intelligent performance summary using Bedrock LLM reasoning.
        
        This demonstrates the AI agent's ability to analyze data and provide insights.
        """
        rows = self._fetch_recent_rows(sku)
        
        # In mock mode, generate a simple summary without calling Bedrock
        inference_mode = os.getenv("MERLIN_INFERENCE_MODE", "local")
        if inference_mode == "local" or not os.getenv("AWS_ACCESS_KEY_ID"):
            # Generate mock summary
            total_units = sum(float(row.get("units_sold", 0)) for row in rows)
            total_revenue = sum(float(row.get("net_revenue_usd", 0)) for row in rows)
            total_ad_spend = sum(float(row.get("ad_spend_usd", 0)) for row in rows)
            acos = (total_ad_spend / total_revenue * 100) if total_revenue > 0 else 0
            
            narrative = f"""📊 Performance Summary for {sku} (Demo Mode)

**7-Day Overview:**
• Total Units Sold: {int(total_units)}
• Total Revenue: ${total_revenue:,.2f}
• Total Ad Spend: ${total_ad_spend:,.2f}
• ACOS: {acos:.1f}%

**Analysis:**
The product shows {('strong' if total_units > 100 else 'moderate')} sales performance with a {'healthy' if acos < 15 else 'high'} advertising cost of sale. 

**Recommendations:**
1. {'Maintain' if acos < 15 else 'Optimize'} current advertising strategy
2. Monitor inventory levels (currently {int(rows[-1].get('inventory_on_hand', 0))} units)
3. Consider {'increasing' if total_units > 100 else 'adjusting'} ad budget based on performance

*Note: This is demo mode with sample data. For real AI analysis, deploy with AWS credentials.*"""
        else:
            # Real Bedrock mode
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
        
        # Check if running in mock mode
        inference_mode = os.getenv("MERLIN_INFERENCE_MODE", "local")
        if inference_mode == "local" or not os.getenv("AWS_ACCESS_KEY_ID"):
            # Generate mock forecast
            import random
            num_predictions = len(feature_payload.get("instances", []))
            if num_predictions == 0:
                num_predictions = 7
            
            mock_predictions = [random.randint(15, 30) for _ in range(num_predictions)]
            logger.info("Returning mock forecast (demo mode)")
            return {
                "predictions": mock_predictions,
                "note": "Demo mode - using mock ML predictions. Deploy with AWS for real forecasts."
            }
        
        logger.info("Requesting forecast from SageMaker")
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
