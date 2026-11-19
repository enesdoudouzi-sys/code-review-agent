"""Integrations-Tests für das FastAPI-Backend."""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from main import app  # noqa: E402

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_leerer_code_gibt_400():
    response = client.post("/review", json={"code": "   ", "dateiname": "test.py"})
    assert response.status_code == 400


def test_fehlender_body_gibt_422():
    response = client.post("/review", json={})
    assert response.status_code == 422


def test_review_erfolg_mit_mock():
    with patch("main.review") as mock_review:
        mock_review.return_value = "## 🔒 Sicherheit\n- Keine Probleme gefunden."
        response = client.post(
            "/review",
            json={"code": "def add(a, b): return a + b", "dateiname": "math.py"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["dateiname"] == "math.py"
    assert "Sicherheit" in data["report"]
    assert data["status"] == "success"
