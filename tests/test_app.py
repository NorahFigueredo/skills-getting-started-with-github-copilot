import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture
def sample_activity(monkeypatch):
    activity = {
        "description": "A test activity",
        "schedule": "Mondays at 3:00 PM",
        "max_participants": 10,
        "participants": [],
    }
    monkeypatch.setitem(activities, "Test Activity", activity)
    return activity


def test_get_activities_includes_current_activities(sample_activity):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Test Activity"] == sample_activity


def test_signup_adds_participant(sample_activity):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@example.com for Test Activity"
    }
    assert sample_activity["participants"] == ["student@example.com"]


def test_signup_rejects_duplicate_participant(sample_activity):
    sample_activity["participants"].append("student@example.com")

    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert sample_activity["participants"] == ["student@example.com"]


def test_signup_returns_not_found_for_unknown_activity():
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(sample_activity):
    sample_activity["participants"].append("student@example.com")

    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Test Activity"
    }
    assert sample_activity["participants"] == []


def test_unregister_returns_not_found_for_unregistered_participant(sample_activity):
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert sample_activity["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity():
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
