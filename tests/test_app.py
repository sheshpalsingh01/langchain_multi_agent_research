import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"topic": ""},
        {"topic": "   "},
        {"topic": "x" * 501},
        ["not", "an", "object"],
    ],
)
def test_research_rejects_invalid_topics(client, payload):
    response = client.post("/research", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_research_requires_api_keys(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    response = client.post("/research", json={"topic": "  climate research  "})

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.get_json()["error"]
