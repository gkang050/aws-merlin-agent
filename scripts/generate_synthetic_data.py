from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

SKU_LIST = ["SKU-001", "SKU-002", "SKU-003"]


def generate_records(days: int) -> list[dict]:
    today = date.today()
    records: list[dict] = []
    for sku in SKU_LIST:
        units = random.randint(5, 20)
        for offset in range(days):
            current_date = today - timedelta(days=offset)
            units = max(1, units + random.randint(-3, 3))
            ad_spend = random.uniform(15, 30)
            record = {
                "seller_id": "demo-seller",
                "sku": sku,
                "date": current_date.isoformat(),
                "units_sold": units,
                "net_revenue": round(units * random.uniform(15, 25), 2),
                "ad_spend": round(ad_spend, 2),
                "inventory_on_hand": random.randint(20, 100),
            }
            records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic MERLIN sample data.")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("data/sample/sales.json"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    records = generate_records(args.days)
    args.output.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
