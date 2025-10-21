# File: /lan-collab/lan-collab/tests/conftest.py

import pytest

@pytest.fixture(scope="session")
def sample_fixture():
    return "sample data"