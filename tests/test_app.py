import pytest
from fastapi.testclient import TestClient


class TestActivitiesEndpoint:
    """Tests for the /activities GET endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check that activities have required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup POST endpoint"""
    
    def test_signup_for_activity(self, client):
        """Test signing up for an activity"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_activity_full(self, client):
        """Test that a student cannot sign up for a full activity"""
        # First, get the activities to find one we can fill
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Find an activity that can be filled quickly for testing
        # Let's use Basketball Team which has max 15 and 1 participant
        activity = "Basketball Team"
        
        # Sign up students until the activity is full
        for i in range(14):  # 14 more students (1 already signed up = 15 total)
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            if response.status_code != 200:
                # Activity might already be full or error
                break
        
        # Try to sign up one more - should fail
        email = "extra@mergington.edu"
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister POST endpoint"""
    
    def test_unregister_participant(self, client):
        """Test unregistering a participant from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Verify participant is in the activity
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister the participant
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant is no longer in the activity
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering a student who is not signed up"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
