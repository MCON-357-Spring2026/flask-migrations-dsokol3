import pytest

from src.migration_exercises.app import create_app
from src.migration_exercises.extensions import db
from src.migration_exercises.models import Assignment, Student, Grade


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


# ===== HOME =====

def test_home(client):
    res = client.get("/exercises/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["message"] == "Flask migrations lesson app"
    assert "endpoints" in data


# ===== STUDENTS =====

def test_create_student(client):
    res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_create_student_missing_name(client):
    res = client.post("/exercises/students", json={"email": "alice@example.com"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_student_missing_email(client):
    res = client.post("/exercises/students", json={"name": "Alice"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_student_missing_both(client):
    res = client.post("/exercises/students", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_list_students(client):
    client.post("/exercises/students", json={"name": "Charlie", "email": "charlie@example.com"})
    client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    client.post("/exercises/students", json={"name": "Bob", "email": "bob@example.com"})

    res = client.get("/exercises/students")
    assert res.status_code == 200
    students = res.get_json()
    assert len(students) == 3


def test_list_students_empty(client):
    res = client.get("/exercises/students")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_students_returns_all_fields(client):
    client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})

    res = client.get("/exercises/students")
    assert res.status_code == 200
    students = res.get_json()
    assert len(students) == 1
    assert students[0]["name"] == "Alice"
    assert students[0]["email"] == "alice@example.com"
    assert "id" in students[0]


# ===== ASSIGNMENTS =====

def test_create_assignment(client):
    res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Quiz 1"
    assert data["max_score"] == 10
    assert "id" in data


def test_create_assignment_missing_title(client):
    res = client.post("/exercises/assignments", json={"max_score": 10})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_assignment_missing_max_score(client):
    res = client.post("/exercises/assignments", json={"title": "Quiz 1"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_assignment_missing_both(client):
    res = client.post("/exercises/assignments", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_list_assignments(client):
    client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    client.post("/exercises/assignments", json={"title": "HW 1", "max_score": 100})

    res = client.get("/exercises/assignments")
    assert res.status_code == 200
    assignments = res.get_json()
    assert len(assignments) == 2


def test_list_assignments_empty(client):
    res = client.get("/exercises/assignments")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_assignments_returns_all_fields(client):
    client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})

    res = client.get("/exercises/assignments")
    assert res.status_code == 200
    assignments = res.get_json()
    assert len(assignments) == 1
    assert assignments[0]["title"] == "Quiz 1"
    assert assignments[0]["max_score"] == 10
    assert "id" in assignments[0]


# ===== GRADES =====

def test_create_grade(client):
    a_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assignment_id = a_res.get_json()["id"]
    s_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    student_id = s_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "student_id": student_id,
        "assignment_id": assignment_id,
        "score": 9
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["score"] == 9
    assert data["student_id"] == student_id
    assert data["assignment_id"] == assignment_id
    assert "id" in data


def test_create_grade_missing_score(client):
    a_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assignment_id = a_res.get_json()["id"]
    s_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    student_id = s_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "student_id": student_id,
        "assignment_id": assignment_id
    })
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_grade_missing_student_id(client):
    a_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assignment_id = a_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "assignment_id": assignment_id,
        "score": 9
    })
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_grade_missing_assignment_id(client):
    s_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    student_id = s_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "student_id": student_id,
        "score": 9
    })
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_grade_missing_all(client):
    res = client.post("/exercises/grades", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_grade_invalid_student_id(client):
    a_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assignment_id = a_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "student_id": 999,
        "assignment_id": assignment_id,
        "score": 9
    })
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_create_grade_invalid_assignment_id(client):
    s_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    student_id = s_res.get_json()["id"]

    res = client.post("/exercises/grades", json={
        "student_id": student_id,
        "assignment_id": 999,
        "score": 9
    })
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_list_grades(client):
    a_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    assignment_id = a_res.get_json()["id"]
    s_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    student_id = s_res.get_json()["id"]

    client.post("/exercises/grades", json={
        "student_id": student_id,
        "assignment_id": assignment_id,
        "score": 9
    })

    res = client.get("/exercises/grades")
    assert res.status_code == 200
    grades = res.get_json()
    assert len(grades) == 1
    assert grades[0]["score"] == 9
    assert grades[0]["student_id"] == student_id
    assert grades[0]["assignment_id"] == assignment_id


def test_list_grades_empty(client):
    res = client.get("/exercises/grades")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_grades_multiple(client):
    a1_res = client.post("/exercises/assignments", json={"title": "Quiz 1", "max_score": 10})
    a1_id = a1_res.get_json()["id"]
    a2_res = client.post("/exercises/assignments", json={"title": "HW 1", "max_score": 100})
    a2_id = a2_res.get_json()["id"]

    s1_res = client.post("/exercises/students", json={"name": "Alice", "email": "alice@example.com"})
    s1_id = s1_res.get_json()["id"]
    s2_res = client.post("/exercises/students", json={"name": "Bob", "email": "bob@example.com"})
    s2_id = s2_res.get_json()["id"]

    client.post("/exercises/grades", json={
        "student_id": s1_id,
        "assignment_id": a1_id,
        "score": 9
    })
    client.post("/exercises/grades", json={
        "student_id": s2_id,
        "assignment_id": a1_id,
        "score": 8
    })
    client.post("/exercises/grades", json={
        "student_id": s1_id,
        "assignment_id": a2_id,
        "score": 95
    })

    res = client.get("/exercises/grades")
    assert res.status_code == 200
    grades = res.get_json()
    assert len(grades) == 3

