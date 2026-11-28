import pytest
import sqlite3
import database

@pytest.fixture(autouse=True)
def setup_table(monkeypatch, tmp_path):
    file_path = tmp_path / "test_golf.db"
    monkeypatch.setattr(database, "DATABASE_PATH", file_path)
    database.init_db()

@pytest.fixture
def connection(setup_table):
    connect = database.get_connection()
    try:
        yield connect
    finally:
        connect.close()

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

@pytest.mark.parametrize("field, value",
                         [
                            ("score", -5),
                            ("gir", 23),
                            ("fairway_hit", 15),
                            ("course_name", ""),
                            ("score", 72.5)
                         ])

# Checks if correct exception will rise when invalid values are submitted
def test_constraints(field, value, connection, sample_round):
    cursor = connection.cursor()
    sample_round[field] = value
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO rounds(
                date, course_name, par, score, putts,
                fairway_hit, fairways_possible, gir, penalty_strokes
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (sample_round["date"], sample_round["course_name"], sample_round["par"], sample_round["score"],
                sample_round["putts"], sample_round["fairway_hit"], sample_round["fairways_possible"],
                sample_round["gir"], sample_round["penalty_strokes"]))

# Checks if rollback works
def test_rollback(connection, sample_round):
    cursor = connection.cursor()
    cursor.execute(
        """INSERT INTO rounds(
            date, course_name, par, score, putts,
            fairway_hit, fairways_possible, gir, penalty_strokes
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (sample_round["date"], sample_round["course_name"], sample_round["par"], sample_round["score"],
                sample_round["putts"], sample_round["fairway_hit"], sample_round["fairways_possible"],
                sample_round["gir"], sample_round["penalty_strokes"]))
    cursor.execute(
            """SELECT * FROM rounds"""
        )
    result = cursor.fetchall()
    assert len(result) == 1
    connection.rollback() 
    cursor.execute(
        """SELECT * FROM rounds"""
    )
    result = cursor.fetchone()
    assert result is None