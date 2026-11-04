import pytest
from household_credit_mcp.backends import SnapshotBackend


@pytest.fixture(scope="session")
def be():
    return SnapshotBackend()
