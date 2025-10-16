"""
Test cases for FastAPI endpoints
"""
import pytest
from fastapi import status
from src.app import activities


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # The redirect should be followed by the test client
        assert "index.html" in str(response.url) or response.is_redirect


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_activities_contains_expected_fields(self, client, reset_activities):
        """Test that each activity contains all expected fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "test@mergington.edu"
        activity_name = "Chess Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Sign up
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert email in updated_participants
    
    def test_signup_duplicate_user(self, client, reset_activities):
        """Test signup with user already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        email = "test@mergington.edu"
        activity_name = "Non-existent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test user can sign up for multiple different activities"""
        email = "test@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify user is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        assert email in initial_participants
        
        # Unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email not in updated_participants
    
    def test_unregister_user_not_registered(self, client, reset_activities):
        """Test unregister user not registered for activity"""
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Student not found" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        email = "test@mergington.edu"
        activity_name = "Non-existent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_and_unregister_cycle(self, client, reset_activities):
        """Test complete cycle of signup and unregister"""
        email = "test@mergington.edu"
        activity_name = "Chess Club"
        
        # Initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        after_signup_response = client.get("/activities")
        after_signup_participants = after_signup_response.json()[activity_name]["participants"]
        assert len(after_signup_participants) == initial_count + 1
        assert email in after_signup_participants
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregistration
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count
        assert email not in final_participants


class TestActivityManagement:
    """Integration tests for activity management"""
    
    def test_activity_capacity_management(self, client, reset_activities):
        """Test that activities track capacity correctly"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])
            
            # Capacity should be positive
            assert max_participants > 0
            # Current participants shouldn't exceed max
            assert current_participants <= max_participants
    
    def test_multiple_users_same_activity(self, client, reset_activities):
        """Test multiple users can sign up for the same activity"""
        activity_name = "Math Olympiad"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Sign up multiple users
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all users are registered
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count + len(emails)
        
        for email in emails:
            assert email in final_participants


class TestParameterValidation:
    """Tests for parameter validation"""
    
    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup works with URL encoding for activity names"""
        # Create a test with an activity that needs URL encoding
        email = "test@mergington.edu"
        activity_name = "Chess Club"  # Contains space
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup works with various email formats"""
        activity_name = "Chess Club"
        
        # Test various email formats
        emails = [
            "test.user@mergington.edu",
            "test+tag@mergington.edu",
            "test_user@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            
            # Clean up for next test
            client.delete(f"/activities/{activity_name}/unregister?email={email}")