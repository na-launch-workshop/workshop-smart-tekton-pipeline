import sqlite3
import pytest
from app.main import greet, get_user


def test_greet_default():
    assert greet() == "Hello, World!"


def test_greet_with_name():
    assert greet("Alice") == "Hello, Alice!"


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "app.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (username TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES ('alice', 'alice@example.com')")
    conn.commit()
    conn.close()
    return db_path


def test_get_user_found(db):
    result = get_user("alice", db_path=db)
    assert result is not None
    assert result[0] == "alice"


def test_get_user_not_found(db):
    result = get_user("nobody", db_path=db)
    assert result is None