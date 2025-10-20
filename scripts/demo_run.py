from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def run(command: list[str]) -> None:
    logger.info("Executing command: %s", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end MERLIN demo helper.")
    parser.add_argument("--env", default="demo")
    args = parser.parse_args()

    run(["python", "scripts/generate_synthetic_data.py"])
    run(["python", "scripts/load_sample_data.py"])
    logger.info("Trigger EventBridge rule or Bedrock workflow manually for environment %s", args.env)
    logger.info("Launch Streamlit with: poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py")


if __name__ == "__main__":
    main()
