"""
Performance and edge case tests for the FastAPI application
"""
import pytest
from fastapi import status
import concurrent.futures
import time


class TestPerformance:
    """Performance tests"""
    
    def test_concurrent_signups(self, client, reset_activities):
        """Test handling concurrent signups to the same activity"""
        activity_name = "Programming Class"
        base_email = "concurrent_test_{i}@mergington.edu"
        num_concurrent = 5
        
        def signup_user(i):
            email = base_email.format(i=i)
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            return response.status_code, email
        
        # Use ThreadPoolExecutor to simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(signup_user, i) for i in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for status_code, email in results:
            assert status_code == status.HTTP_200_OK
        
        # Verify all users are registered
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        for i in range(num_concurrent):
            email = base_email.format(i=i)
            assert email in participants
    
    def test_api_response_time(self, client, reset_activities):
        """Test that API responses are reasonably fast"""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 1.0  # Should respond within 1 second


class TestEdgeCases:
    """Edge case tests"""
    
    def test_empty_email_parameter(self, client, reset_activities):
        """Test signup with empty email parameter"""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email=")
        # The API should handle this gracefully - either reject or accept based on business logic
        # For now, we'll just ensure it doesn't crash
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_missing_email_parameter(self, client, reset_activities):
        """Test signup without email parameter"""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_extremely_long_email(self, client, reset_activities):
        """Test signup with extremely long email"""
        activity_name = "Chess Club"
        long_email = "a" * 1000 + "@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={long_email}")
        # Should either accept or reject gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_special_characters_in_activity_name(self, client, reset_activities):
        """Test with URL-encoded special characters in activity name"""
        import urllib.parse
        
        # Test activity name with spaces (should work since "Chess Club" exists)
        activity_name = urllib.parse.quote("Chess Club")
        email = "test@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
    
    def test_case_sensitivity_activity_names(self, client, reset_activities):
        """Test case sensitivity of activity names"""
        email = "test@mergington.edu"
        
        # Test exact case (should work)
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        
        # Clean up
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Test different case (should fail)
        response2 = client.post(f"/activities/chess club/signup?email={email}")
        assert response2.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unicode_in_email(self, client, reset_activities):
        """Test unicode characters in email"""
        activity_name = "Chess Club"
        unicode_email = "test.üñíçødé@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={unicode_email}")
        # Should handle unicode gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestDataIntegrity:
    """Data integrity tests"""
    
    def test_activity_data_persistence_across_requests(self, client, reset_activities):
        """Test that activity data persists across multiple requests"""
        email = "persistence_test@mergington.edu"
        activity_name = "Chess Club"
        
        # Sign up user
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        
        # Make multiple requests to verify data persists
        for _ in range(5):
            response = client.get("/activities")
            assert response.status_code == status.HTTP_200_OK
            participants = response.json()[activity_name]["participants"]
            assert email in participants
    
    def test_activity_structure_consistency(self, client, reset_activities):
        """Test that all activities have consistent structure"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        activities_data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities_data.items():
            # Check all required fields exist
            for field in required_fields:
                assert field in activity_data, f"Field {field} missing in {activity_name}"
            
            # Check field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check constraints
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]


class TestErrorHandling:
    """Error handling tests"""
    
    def test_malformed_requests(self, client, reset_activities):
        """Test various malformed requests"""
        # Test with malformed activity name paths
        response1 = client.post("/activities//signup?email=test@mergington.edu")
        assert response1.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # Test with malformed endpoints
        response2 = client.post("/activities/Chess%20Club/signup/extra?email=test@mergington.edu")
        assert response2.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unsupported_http_methods(self, client, reset_activities):
        """Test unsupported HTTP methods on endpoints"""
        # GET on signup endpoint (should fail)
        response1 = client.get("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response1.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # POST on unregister endpoint (should fail)
        response2 = client.post("/activities/Chess Club/unregister?email=test@mergington.edu")
        assert response2.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # PUT on activities endpoint (should fail)
        response3 = client.put("/activities")
        assert response3.status_code == status.HTTP_405_METHOD_NOT_ALLOWED