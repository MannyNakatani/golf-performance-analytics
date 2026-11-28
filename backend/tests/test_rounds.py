import pytest
import main
import database
from fastapi.testclient import TestClient

# Resets the database for testing
@pytest.fixture(autouse=True)
def setup_test_database(tmp_path, monkeypatch):
    file_path = tmp_path / "test_golf.db"
    monkeypatch.setattr(database, "DATABASE_PATH", file_path)

# Makes sure that set_up_database runs first.
# yielding allow us to intreact with API without closing
@pytest.fixture()
def client(setup_test_database):
    with TestClient(main.app) as test_client:
        yield test_client

@pytest.fixture
def sample_round():
    return {
        "date": "2026-11-25",
        "course_name": "University of Maryland Golf Course",
        "par": 71,
        "score": 69,
        "putts": 28,
        "fairway_hit": 10,
        "fairways_possible": 14,
        "gir": 13,
        "penalty_strokes": 0
    }

@pytest.fixture
def existing_round(sample_round, client):
    response = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 201
    return response.json()

def assert_round_matches(existing_round, client):
    response = client.get(f"/api/v1/rounds/{existing_round['id']}")
    assert response.status_code == 200
    assert response.json() == existing_round

# Checks if we can retieve a rounds list when the list is empty.
def test_get_empty_rounds(client):
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert response.json() == []

# Checks if we are able to submit a new round.
def test_create_round(sample_round, client):
    response = client.post("/api/v1/rounds", json=sample_round)
    body = response.json()
    assert response.status_code == 201
    assert body == {"id": 1, **sample_round}

# Checks if we can retrieve a rounds list when the list is non-empty.
def test_get_all_rounds(existing_round, client):
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert response.json() == [existing_round]

# Checks if we can retrieve a specific round.
def test_get_specific_round(existing_round, client):
    assert_round_matches(existing_round, client)

# Checks if we will get a 404 error when we try to retrieve a round that does not exist.
def test_get_nonexistent_round(client):
    response = client.get("/api/v1/rounds/2")
    assert response.status_code == 404
    assert response.json()["detail"] == "Round not found"

@pytest.mark.parametrize("field, value",
                         [
                            ("gir", 0),
                            ("gir", 18),
                            ("fairway_hit", 0),
                            ("fairway_hit", 14),
                            ("penalty_strokes", 0)
                         ])

# Checks if submitting a round with values on the boundary still works as intended.
def test_valid_boundary(field, value, sample_round, client):
    sample_round[field] = value
    response = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 201
    assert response.json()[field] == value
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.parametrize("field, invalid_value", 
                         [
                            ("score", -5),
                            ("gir", 19),
                            ("par", 0),
                            ("putts", -1),
                            ("fairway_hit", -1),
                            ("fairways_possible", 19),
                            ("course_name", ""),
                            ("score", "71"),
                            ("score", 72.5),
                            ("penalty_strokes", -1)
                          ])

# Checks if we will get a 422 error and that the round is not actually submitted when we
# try to submit a round with invalid fields.
def test_invalid_field(field, invalid_value, sample_round, client):
    sample_round[field] = invalid_value
    response = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 422
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 0

# Checks if we will get a 422 error and that the round is not actually submitted when we try 
# to submit a score with more fairway hits than number of fairways.
def test_invalid_fairways(sample_round, client):
    sample_round["fairway_hit"] = 15
    sample_round["fairways_possible"] = 14
    response = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 422
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 0

# Checks if we will get a 422 error and that the round is not actually submitted when we try 
# to submit a round with no score.
def test_missing_score(sample_round, client):
    del sample_round["score"]
    response = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 422
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 0

# Checks if we can edit a round successfully without adding a new round instead.
def test_update_round(existing_round, sample_round, client):
    sample_round["score"] = 75
    sample_round["putts"] = 32
    response = client.put(f"/api/v1/rounds/{existing_round['id']}", json=sample_round)
    body = response.json()
    assert response.status_code == 200
    assert body["score"] == 75
    assert body["putts"] == 32
    assert body["id"] == existing_round["id"]
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_round_matches(body, client)

# Checks if trying to edit a nonexistent round will give us 404 error and no round is
# added to the round list
def test_update_nonexistent_round(sample_round, client):
    response = client.put(f"/api/v1/rounds/999", json=sample_round)
    assert response.status_code == 404
    assert response.json()["detail"] == "Round not found"
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 0

# Checks if trying to edit a score to an invalid score will give us 422 errror and 
# the original round is not modified.
def test_invalid_update(existing_round, sample_round, client):
    sample_round["score"] = -10
    response = client.put(f"/api/v1/rounds/{existing_round['id']}", json=sample_round)
    assert response.status_code == 422
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_round_matches(existing_round, client)

# Checks if we can successfully delete a round with 204 code and if trying to retrieve
# that round afterwards will give us 404 error.
def test_delete_round(existing_round, client):
    response = client.delete(f"/api/v1/rounds/{existing_round['id']}")
    response2 = client.get(f"/api/v1/rounds/{existing_round['id']}")
    assert response.status_code == 204
    assert response.content == b""
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 0
    assert response2.status_code == 404

# Checks that trying to delete a nonexistent round will give us 404 error and that 
# other existing round won't be effected
def test_delete_nonexistent_round(existing_round, client):
    response = client.delete("/api/v1/rounds/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Round not found"
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Checks if the deletion will work properly, and if adding a new round after deleteion
# will not reuse the same id.
def test_deleted_id_not_reused(existing_round, sample_round, client):
    response = client.delete(f"/api/v1/rounds/{existing_round['id']}")
    response2 = client.post("/api/v1/rounds", json=sample_round)
    assert response.status_code == 204
    assert response2.status_code == 201
    assert existing_round["id"] < response2.json()["id"]
    response = client.get("/api/v1/rounds")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Checks if we can access the data we submitted after restarting the API
def test_database_persistence(sample_round):
    with TestClient(main.app) as test_client1:
        response = test_client1.post("/api/v1/rounds", json=sample_round)
        assert response.status_code == 201
        response = test_client1.get("/api/v1/rounds")
        assert response.status_code == 200
        assert len(response.json()) == 1
        test_round = response.json()[0]
    with TestClient(main.app) as test_client2:
        response = test_client2.get("/api/v1/rounds")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert test_round == response.json()[0]