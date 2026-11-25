import json
from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from main import app

SUMMARY_URL = "/api/v1/analytics/score-summary"


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([72, 75, 68, 73, 70], (5, 71.6, 68, 75, 7)),
        ([72], (1, 72, 72, 72, 0)),
        ([71, 71, 71], (3, 71, 71, 71, 0)),
        ([70] * 100, (100, 70, 70, 70, 0)),
    ],
)
def test_score_summary(
    client: TestClient, scores: list[int], expected: tuple[int, float, int, int, int]
) -> None:
    count, average, best, worst, score_range = expected
    response = client.post(SUMMARY_URL, json={"scores": scores})

    assert response.status_code == 200
    assert response.json() == {
        "round_count": count,
        "scoring_average": average,
        "best_score": best,
        "worst_score": worst,
        "score_range": score_range,
    }


def test_score_summary_preserves_large_numeric_average(client: TestClient) -> None:
    score = 10**400
    response = client.post(SUMMARY_URL, json={"scores": [score, score + 1]})

    assert response.status_code == 200
    body = json.loads(response.content, parse_float=Decimal)
    assert body["scoring_average"] == Decimal(f"{score}.5")
    assert body["score_range"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"scores": []},
        {"scores": [72] * 101},
        {"scores": [0]},
        {"scores": [72, -1]},
        {"scores": ["72"]},
        {"scores": [True]},
        {"scores": [72.0]},
        {"scores": [None]},
        {"scores": 72},
        {"scores": None},
        {},
    ],
)
def test_score_summary_rejects_invalid_requests(
    client: TestClient, payload: dict[str, object]
) -> None:
    response = client.post(SUMMARY_URL, json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][:2] == ["body", "scores"]


def test_score_summary_is_documented(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"][SUMMARY_URL]["post"]
    models = schema["components"]["schemas"]

    for content, model in [
        (operation["requestBody"]["content"], "ScoreSummaryRequest"),
        (operation["responses"]["200"]["content"], "ScoreSummaryResponse"),
    ]:
        assert content["application/json"]["schema"]["$ref"] == f"#/components/schemas/{model}"
    assert models["ScoreSummaryResponse"]["properties"]["scoring_average"]["type"] == "number"
