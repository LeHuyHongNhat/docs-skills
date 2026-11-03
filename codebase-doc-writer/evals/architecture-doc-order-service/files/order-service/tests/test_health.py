from fastapi.testclient import TestClient


def test_health(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("JWT_SECRET", "x")
    from app.main import app
    assert TestClient(app).get("/health").json() == {"status": "ok"}
