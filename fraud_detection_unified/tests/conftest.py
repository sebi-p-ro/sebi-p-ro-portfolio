"""Pytest configuration for fraud detection tests."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "velocity_threshold": 10,
        "high_value_threshold": 500000,
        "ml_fraud_threshold": 0.7,
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "streaming: mark test as streaming-related"
    )
