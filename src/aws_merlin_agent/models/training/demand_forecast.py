from __future__ import annotations

import argparse

import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from aws_merlin_agent.features.engineering import build_feature_frame
from aws_merlin_agent.utils.logging import get_logger

logger = get_logger(__name__)


def train(input_path: str, model_output: str) -> float:
    """Train a simple demand forecast model and persist artifacts for SageMaker deployment."""
    logger.info("Loading training data from %s", input_path)
    df = pd.read_parquet(input_path)
    features = build_feature_frame(df)
    features["lag_days"] = range(len(features))
    y = features["units_sold"].astype(float)
    X = features.drop(columns=["units_sold"]).select_dtypes(include=["number"]).fillna(0.0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
    )
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    logger.info("Validation R^2: %.3f", score)
    model.save_model(model_output)
    logger.info("Persisted model artifact to %s", model_output)
    return float(score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train demand forecast model.")
    parser.add_argument("--input", required=True, help="Path to curated parquet dataset")
    parser.add_argument("--output", required=True, help="Path to write XGBoost model artifact")
    args = parser.parse_args()
    train(args.input, args.output)
