import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    from moto import mock_aws  # type: ignore[attr-defined]
except ImportError:
    from moto import mock_dynamodb as _mock_dynamodb  # type: ignore[attr-defined]
    from moto import mock_s3 as _mock_s3  # type: ignore[attr-defined]

    @contextmanager
    def mock_aws():
        with _mock_s3():
            with _mock_dynamodb():
                yield


@pytest.fixture(scope="function")
def dummy_settings(monkeypatch):
    monkeypatch.setenv("MERLIN_ENV", "test")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("MERLIN_DATA_LAKE_BUCKET", "merlin-test-landing")
    monkeypatch.setenv("MERLIN_CURATED_BUCKET", "merlin-test-curated")
    monkeypatch.setenv("MERLIN_CREATIVE_BUCKET", "merlin-test-creative")
    monkeypatch.setenv("MERLIN_RUNS_TABLE", "merlin-test-runs")
    monkeypatch.setenv("MERLIN_ACTIONS_TABLE", "merlin-test-actions")
    yield


@pytest.fixture
def moto_aws():
    with mock_aws():
        yield
