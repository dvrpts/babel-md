from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Patch the converter before importing the app so lifespan doesn't load ML models
with patch("babel_md.main.get_converter"):
    from babel_md.main import app

from babel_md.converter import get_converter


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _clear_converter_cache():
    get_converter.cache_clear()
    yield
    get_converter.cache_clear()
