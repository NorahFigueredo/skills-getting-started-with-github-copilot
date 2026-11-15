from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_unregister_removes_participant(monkeypatch):
    activity = {"participants": ["student@example.com"]}
    monkeypatch.setitem(activities, "Test Activity", activity)

    response = client.delete(
        "/activities/Test%20Activity/signup?email=student%40example.com"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Test Activity"
    }
    assert activity["participants"] == []


def test_unregister_returns_not_found_for_unregistered_participant(monkeypatch):
    activity = {"participants": []}
    monkeypatch.setitem(activities, "Test Activity", activity)

    response = client.delete(
        "/activities/Test%20Activity/signup?email=student%40example.com"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity["participants"] == []
