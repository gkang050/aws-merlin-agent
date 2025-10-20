from __future__ import annotations

import json
from typing import List, Dict

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws
from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def summarize_rows(rows: List[Dict[str, str]]) -> str:
    """
    Use Amazon Bedrock (Nova or Claude) to generate intelligent narrative summaries from KPI data.
    
    This implements the required LLM reasoning component for the hackathon.
    """
    if not rows:
        return "No recent data available."
    
    settings = EnvironmentSettings.load()
    bedrock_runtime = aws.client("bedrock-runtime", region_name=settings.region)
    
    # Calculate basic metrics for context
    total_units = sum(float(row.get("units_sold", 0)) for row in rows)
    total_revenue = sum(float(row.get("net_revenue_usd", 0)) for row in rows)
    total_ad_spend = sum(float(row.get("ad_spend_usd", 0)) for row in rows)
    
    # Prepare data for LLM analysis
    data_summary = {
        "period_days": len(rows),
        "total_units_sold": int(total_units),
        "total_revenue_usd": round(total_revenue, 2),
        "total_ad_spend_usd": round(total_ad_spend, 2),
        "daily_data": rows[:7]  # Include recent daily breakdown
    }
    
    prompt = f"""You are MERLIN, an AI agent helping Amazon marketplace sellers optimize their business.

Analyze this sales performance data and provide actionable insights:

{json.dumps(data_summary, indent=2)}

Provide a concise analysis covering:
1. Overall performance trend
2. Key metrics (units sold, revenue, advertising efficiency)
3. Specific recommendations for improvement
4. Any concerning patterns or opportunities

Keep your response focused and actionable for a busy seller."""

    try:
        # Try Amazon Nova Pro first (preferred for hackathon)
        model_id = "amazon.nova-pro-v1:0"
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        summary = response_body["output"]["message"]["content"][0]["text"]
        logger.info("Generated Bedrock summary using %s", model_id)
        
    except Exception as e:
        logger.warning("Nova Pro failed (%s), falling back to Claude", str(e))
        try:
            # Fallback to Claude 3 Sonnet
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response["body"].read())
            summary = response_body["content"][0]["text"]
            logger.info("Generated Bedrock summary using Claude fallback")
            
        except Exception as fallback_error:
            logger.error("Both Nova and Claude failed: %s", str(fallback_error))
            # Provide basic summary as last resort
            avg_acos = (total_ad_spend / total_revenue * 100) if total_revenue > 0 else 0
            summary = (
                f"Performance Summary ({len(rows)} days):\n"
                f"• Units Sold: {int(total_units)}\n"
                f"• Revenue: ${total_revenue:,.2f}\n"
                f"• Ad Spend: ${total_ad_spend:,.2f}\n"
                f"• ACOS: {avg_acos:.1f}%\n"
                f"Note: LLM analysis unavailable - check Bedrock model access."
            )
    
    return summary
