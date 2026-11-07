import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="cybbig-test-"))
os.environ.setdefault("CYBBIG_DATA_DIR", str(_TMP))
os.environ.setdefault("CYBBIG_DB_PATH", str(_TMP / "cybbig.db"))
# Le moteur IA de fond appellerait le vrai Ollama du poste pendant les tests.
os.environ.setdefault("CYBBIG_AI_WORKER", "0")

from fastapi.testclient import TestClient

import pytest

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def consented(client):
    status = client.get("/api/consent").json()
    if not status.get("accepted"):
        response = client.post("/api/consent", json={
            "accepted": True,
            "user_name": "Test local",
            "organization": "Cybbig Tests",
            "purpose": "Vérification automatisée",
        })
        assert response.status_code == 200
    return client


@pytest.fixture(scope="session")
def project(consented):
    projects = consented.get("/api/projects").json()["items"]
    assert projects
    return projects[0]
