from __future__ import annotations

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def ensure_dataset() -> str:
    """Create (or return) the QuickSight dataset ARN used for dashboard visualizations."""
    settings = EnvironmentSettings.load()
    _qs = aws.client("quicksight", region_name=settings.region)  # Reserved for future API calls
    dataset_id = f"merlin-{settings.env}-sales-dataset"
    logger.info("Ensuring QuickSight dataset %s", dataset_id)
    # Placeholder: in MVP we simply return the identifier; real implementation should call create_data_set.
    return dataset_id
