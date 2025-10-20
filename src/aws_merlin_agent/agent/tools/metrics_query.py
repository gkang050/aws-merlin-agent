from __future__ import annotations

import json
from typing import Any, Dict

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def run_kpi_query(sql: str, *, max_results: int = 50) -> list[Dict[str, Any]]:
    """Execute the provided SQL string against Athena and return result rows as dicts."""
    settings = EnvironmentSettings.load()
    athena = aws.client("athena", region_name=settings.region)
    s3_output = f"s3://{settings.curated_bucket}/athena-results/"
    logger.info("Submitting Athena query to %s", s3_output)
    query_execution = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": f"merlin_{settings.env}"},
        ResultConfiguration={"OutputLocation": s3_output},
    )
    execution_id = query_execution["QueryExecutionId"]
    waiter = athena.get_waiter("query_execution_complete")
    waiter.wait(QueryExecutionId=execution_id)
    result = athena.get_query_results(QueryExecutionId=execution_id, MaxResults=max_results)
    rows = result["ResultSet"].get("Rows", [])
    column_info = result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    column_names = [col["Name"] for col in column_info]
    parsed: list[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if idx == 0 and all(cell.get("VarCharValue") for cell in row["Data"]):
            # Header row; skip
            continue
        data = row.get("Data", [])
        if not data:
            continue
        record: Dict[str, Any] = {}
        for col_name, cell in zip(column_names, data):
            record[col_name] = cell.get("VarCharValue")
        if record:
            parsed.append(record)
    logger.debug("Athena rows returned: %s", json.dumps(parsed))
    return parsed
