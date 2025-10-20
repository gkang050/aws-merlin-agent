from __future__ import annotations

import pandas as pd


def build_feature_frame(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich seller data with derived features used by forecasting and optimization models.

    Expected columns: seller_id, sku, date, units_sold, net_revenue, ad_spend, inventory_on_hand.
    """
    df = sales_df.copy()
    df["revenue_per_unit"] = df["net_revenue"] / df["units_sold"].clip(lower=1)
    df["ad_efficiency"] = df["net_revenue"] / df["ad_spend"].replace({0: pd.NA})
    df["stockout_risk"] = df["units_sold"].rolling(window=7, min_periods=1).sum() / df["inventory_on_hand"].replace(
        {0: pd.NA}
    )
    return df.fillna(0.0)
