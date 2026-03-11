import pytest

from src.migration_exercises.app import create_app
from src.migration_exercises.extensions import db


@pytest.fixture()
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _create_student(client, name="Ava", email="ava@example.com"):
    res = client.post(
        "/exercises/students",
        json={"name": name, "email": email},
    )
    assert res.status_code == 201
    return res.get_json()["id"]


def _create_assignment(client, title="ORM Practice", max_score=100, due_date=None):
    payload = {"title": title, "max_score": max_score}
    if due_date is not None:
        payload["due_date"] = due_date

    res = client.post("/exercises/assignments", json=payload)
    return res


def _create_grade(client, student_id, assignment_id, score=95, comment=None):
    payload = {
        "score": score,
        "student_id": student_id,
        "assignment_id": assignment_id,
    }
    if comment is not None:
        payload["comment"] = comment

    res = client.post("/exercises/grades", json=payload)
    return res


# --- Assignment due_date (TODO 5, TODO 8, TODO 10) ---

def test_post_assignment_accepts_due_date_and_returns_it(client):
    res = _create_assignment(client, due_date="2026-04-01")
    assert res.status_code == 201

    data = res.get_json()
    assert data["title"] == "ORM Practice"
    assert data["max_score"] == 100
    assert "due_date" in data
    assert data["due_date"] == "2026-04-01"


def test_post_assignment_without_due_date_returns_none(client):
    res = _create_assignment(client)
    assert res.status_code == 201

    data = res.get_json()
    assert "due_date" in data
    assert data["due_date"] is None


def test_get_assignments_includes_due_date_field(client):
    _create_assignment(client, title="A1", due_date="2026-04-01")
    _create_assignment(client, title="A2")  # no due_date

    res = client.get("/exercises/assignments")
    assert res.status_code == 200

    rows = res.get_json()
    assert len(rows) == 2
    assert "due_date" in rows[0]
    assert "due_date" in rows[1]

    by_title = {row["title"]: row for row in rows}
    assert by_title["A1"]["due_date"] == "2026-04-01"
    assert by_title["A2"]["due_date"] is None


def test_post_assignment_invalid_due_date_rejected(client):
    # If route validation is implemented, this should be 400.
    # If not implemented yet, this test will correctly fail for autograding.
    res = _create_assignment(client, due_date="2026-99-99")
    assert res.status_code == 400
    body = res.get_json()
    assert isinstance(body, dict)
    assert "error" in body


# --- Grade comment (TODO 6, TODO 9, TODO 11) ---

def test_post_grade_accepts_comment_and_returns_it(client):
    student_id = _create_student(client)
    assignment_res = _create_assignment(client, due_date="2026-04-01")
    assignment_id = assignment_res.get_json()["id"]

    res = _create_grade(
        client,
        student_id=student_id,
        assignment_id=assignment_id,
        score=95,
        comment="Great improvement from last week",
    )
    assert res.status_code == 201

    data = res.get_json()
    assert data["score"] == 95
    assert "comment" in data
    assert data["comment"] == "Great improvement from last week"


def test_post_grade_without_comment_returns_none(client):
    student_id = _create_student(client)
    assignment_res = _create_assignment(client)
    assignment_id = assignment_res.get_json()["id"]

    res = _create_grade(
        client,
        student_id=student_id,
        assignment_id=assignment_id,
        score=88,
    )
    assert res.status_code == 201

    data = res.get_json()
    assert "comment" in data
    assert data["comment"] is None


def test_get_grades_includes_comment_field(client):
    student_id = _create_student(client)
    assignment_res = _create_assignment(client, due_date="2026-04-01")
    assignment_id = assignment_res.get_json()["id"]

    _create_grade(
        client,
        student_id=student_id,
        assignment_id=assignment_id,
        score=95,
        comment="Excellent work",
    )
    _create_grade(
        client,
        student_id=student_id,
        assignment_id=assignment_id,
        score=80,
    )

    res = client.get("/exercises/grades")
    assert res.status_code == 200
    rows = res.get_json()
    assert len(rows) == 2

    assert "comment" in rows[0]
    assert "comment" in rows[1]

    comments = {row["score"]: row["comment"] for row in rows}
    assert comments[95] == "Excellent work"
    assert comments[80] is None
