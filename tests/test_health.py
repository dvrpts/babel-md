from unittest.mock import patch

from fastapi.testclient import TestClient

# Patch the converter before importing the app so lifespan doesn't load ML models
with patch("babel_md.main.get_converter"):
    from babel_md.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
