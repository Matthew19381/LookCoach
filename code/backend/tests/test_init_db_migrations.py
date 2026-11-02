"""Plan 7.8 (D14): init_db migrates fresh and pre-Alembic databases, idempotently."""
import sqlite3

from sqlalchemy import create_engine, inspect

from backend import database


def _init(monkeypatch, path):
    url = f"sqlite:///{path}"
    monkeypatch.setattr(database, "DATABASE_URL", url)
    monkeypatch.setattr(database, "engine", create_engine(url))
    database.init_db()
    database.init_db()  # second start: nothing to do, no error
    return set(inspect(database.engine).get_table_names())


def test_fresh_database_gets_every_table(tmp_path, monkeypatch):
    from backend.models.base import Base
    import backend.models  # noqa: F401

    tables = _init(monkeypatch, tmp_path / "fresh.db")
    assert set(Base.metadata.tables) <= tables and "alembic_version" in tables


def test_pre_alembic_database_keeps_data_and_gets_missing_parts(tmp_path, monkeypatch):
    path = tmp_path / "legacy.db"
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR, created_at DATETIME);
        CREATE TABLE photos (id INTEGER PRIMARY KEY, user_id INTEGER, photo_type VARCHAR(10),
            file_path VARCHAR(255), uploaded_at DATETIME, analysis_status VARCHAR(20));
        CREATE TABLE analyses (id INTEGER PRIMARY KEY, photo_id INTEGER, face_data TEXT, body_data TEXT,
            skin_data TEXT, hair_data TEXT, attractiveness_lever TEXT, created_at DATETIME, overall_score FLOAT);
        CREATE TABLE user_profiles (id INTEGER PRIMARY KEY, user_id INTEGER, goals TEXT, lifestyle TEXT,
            discipline_score INTEGER);
        CREATE TABLE recommendations (id INTEGER PRIMARY KEY, user_id INTEGER);
        CREATE TABLE progress_logs (id INTEGER PRIMARY KEY, user_id INTEGER);
        CREATE TABLE experiments (id INTEGER PRIMARY KEY, user_id INTEGER);
        CREATE TABLE integration_events (id INTEGER PRIMARY KEY, user_id VARCHAR);
        CREATE TABLE outbox_events (id INTEGER PRIMARY KEY, user_id INTEGER, event_type VARCHAR, data TEXT,
            timestamp VARCHAR, status VARCHAR, attempts INTEGER, next_attempt_at DATETIME, last_error TEXT,
            hub_response TEXT, created_at DATETIME, sent_at DATETIME);
        INSERT INTO photos (user_id, photo_type, file_path) VALUES (1, 'front', 'uploads/a.jpg');
    """)
    con.commit()
    con.close()

    tables = _init(monkeypatch, path)
    assert {"push_subscriptions", "assistant_messages", "adherence_logs"} <= tables
    con = sqlite3.connect(path)
    assert con.execute("select count(*) from photos").fetchone()[0] == 1
    cols = [r[1] for r in con.execute("pragma table_info(user_profiles)")]
    assert "health" in cols and "mode" in cols
    assert "overall_score" not in [r[1] for r in con.execute("pragma table_info(analyses)")]
