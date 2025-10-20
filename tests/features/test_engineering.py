import pandas as pd

from aws_merlin_agent.features.engineering import build_feature_frame


def test_feature_engineering_creates_expected_columns():
    df = pd.DataFrame(
        {
            "seller_id": ["s1"],
            "sku": ["sku"],
            "date": ["2024-01-01"],
            "units_sold": [10],
            "net_revenue": [200.0],
            "ad_spend": [20.0],
            "inventory_on_hand": [50],
        }
    )
    enriched = build_feature_frame(df)
    assert set(["revenue_per_unit", "ad_efficiency", "stockout_risk"]).issubset(enriched.columns)
