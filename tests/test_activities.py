"""Tests for the Mergington High School activities API."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that GET /activities contains expected activities."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Robotics Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = [
            "description",
            "schedule",
            "max_participants",
            "participants"
        ]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_valid_activity_returns_200(self, client):
        """Test successful signup for a valid activity."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newalex@mergington.edu"}
        )
        result = response.json()
        assert "message" in result
        assert "newalex@mergington.edu" in result["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds the participant to the activity."""
        email = "testuser@mergington.edu"
        
        # Get initial participants count
        response1 = client.get("/activities")
        initial_participants = len(response1.json()["Tennis Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        # Get updated participants count
        response2 = client.get("/activities")
        updated_participants = len(response2.json()["Tennis Club"]["participants"])
        
        assert updated_participants == initial_participants + 1

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice for same activity returns 400."""
        email = "duplicate@mergington.edu"
        activity = "Drama Club"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Attempt duplicate signup
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_signup_different_activities(self, client):
        """Test that same student can sign up for multiple activities."""
        email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200


class TestRoot:
    """Test the root endpoint."""

    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static index."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
