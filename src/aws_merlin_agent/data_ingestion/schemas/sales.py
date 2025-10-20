from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class SalesRecord(BaseModel):
    """Schema for a single seller sales record ingested via API or batch upload."""

    seller_id: str = Field(..., description="Pseudonymized seller identifier")
    sku: str
    date: date
    units_sold: int = Field(..., ge=0)
    net_revenue: float = Field(..., ge=0)
    ad_spend: Optional[float] = Field(default=None, ge=0)
    inventory_on_hand: Optional[int] = Field(default=None, ge=0)
