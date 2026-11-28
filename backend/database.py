import sqlite3
from pathlib import Path
from schemas import RoundCreate, RoundResponse

DATABASE_PATH = Path(__file__).resolve().parent / "golf.db"

# Configure to allow access of values by col name, and allow
# converting to dictionary
def get_connection() -> sqlite3.Connection:
    connect = sqlite3.connect(DATABASE_PATH)
    connect.row_factory = sqlite3.Row
    return connect

# Inserts a round into the database and returns the created round.
def create_round(new_round: RoundCreate) -> RoundResponse:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute(
            """INSERT INTO rounds(
                date, course_name, par, score, putts,
                fairway_hit, fairways_possible, gir, penalty_strokes
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (new_round.date.isoformat(), new_round.course_name, new_round.par, new_round.score,
             new_round.putts, new_round.fairway_hit, new_round.fairways_possible,
             new_round.gir, new_round.penalty_strokes))
        round_id = cursor.lastrowid
        response = RoundResponse(id=round_id, **new_round.model_dump())
        connect.commit()
        return response
    except Exception:
        connect.rollback()
        raise
    finally:
        connect.close()

# Retreieves all rounds from the database and returns them as a list.
def get_rounds() -> list[RoundResponse]:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute("""
            SELECT * FROM rounds ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        all_rounds = [RoundResponse(**dict(row)) for row in rows]
        return all_rounds
    finally:
        connect.close()
        
# Retrieves a round with a given id from the database and returns it.
def get_round(round_id: int) -> RoundResponse | None:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute(
            """SELECT * FROM rounds WHERE id = ?""",
            (round_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return RoundResponse(**dict(row))
    finally:
        connect.close()

# Updates a specific round
def update_round(round_id: int, updated_round: RoundCreate)  -> RoundResponse | None:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute("""
            UPDATE rounds
            SET date = ?,
                course_name = ?,
                par = ?,
                score = ?, 
                putts = ?,
                fairway_hit = ?, 
                fairways_possible = ?, 
                gir = ?, 
                penalty_strokes = ?
            WHERE id = ?""",
            (updated_round.date.isoformat(), updated_round.course_name, updated_round.par,
            updated_round.score, updated_round.putts, updated_round.fairway_hit,
            updated_round.fairways_possible, updated_round.gir, updated_round.penalty_strokes, round_id)
        )
        valid = cursor.rowcount
        if valid == 0:
            connect.rollback()
            return None
        response = RoundResponse(id=round_id, **updated_round.model_dump())
        connect.commit()
        return response
    except Exception:
        connect.rollback()
        raise
    finally:
        connect.close()

# Deletes a specific round
def delete_round(round_id: int) -> bool:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute(
            """DELETE FROM rounds WHERE id = ?""",
            (round_id,))
        valid = cursor.rowcount
        if valid == 0:
            connect.rollback()
            return False
        connect.commit()
        return True
    except Exception:
        connect.rollback()
        raise
    finally:
        connect.close()

# We use try and finally to make sure that we can close the connection
# no matter what.
def init_db() -> None:
    connect = get_connection()
    try:
        cursor = connect.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rounds(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                course_name TEXT NOT NULL CHECK(length(course_name) > 0),
                par INTEGER NOT NULL CHECK(par > 0),
                score INTEGER NOT NULL CHECK(score > 0),
                putts INTEGER NOT NULL CHECK(putts >= 0),
                fairway_hit INTEGER NOT NULL CHECK(fairway_hit BETWEEN 0 AND 18),
                fairways_possible INTEGER NOT NULL CHECK(fairways_possible BETWEEN 0 AND 18),
                gir INTEGER NOT NULL CHECK(gir BETWEEN 0 AND 18),
                penalty_strokes INTEGER NOT NULL CHECK(penalty_strokes >= 0),
                CHECK (fairway_hit <= fairways_possible)
            ) STRICT
        """)
        connect.commit()
    except Exception:
        connect.rollback()
        raise
    finally:
        connect.close()

if __name__ == "__main__":
    init_db()