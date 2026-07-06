"""
Tests for the Mergington High School API.
Structured using the Arrange-Act-Assert (AAA) pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange — no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_non_empty_dict(self, client):
        # Arrange — no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_have_expected_structure(self, client):
        # Arrange — no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant_to_list(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        email = "michael@mergington.edu"  # already signed up for Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange
        email = "michael@mergington.edu"  # already signed up for Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant_from_list(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_not_signed_up_returns_404(self, client):
        # Arrange
        email = "notstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
