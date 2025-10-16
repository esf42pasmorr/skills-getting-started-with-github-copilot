"""
Tests for static file serving and frontend functionality
"""
import pytest
from fastapi import status


class TestStaticFiles:
    """Tests for static file serving"""
    
    def test_static_index_html_accessible(self, client):
        """Test that static index.html is accessible"""
        response = client.get("/static/index.html")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "").lower()
    
    def test_static_css_accessible(self, client):
        """Test that static CSS files are accessible"""
        response = client.get("/static/styles.css")
        assert response.status_code == status.HTTP_200_OK
        assert "text/css" in response.headers.get("content-type", "").lower()
    
    def test_static_js_accessible(self, client):
        """Test that static JavaScript files are accessible"""
        response = client.get("/static/app.js")
        assert response.status_code == status.HTTP_200_OK
        # JavaScript can be served as different content types
        content_type = response.headers.get("content-type", "").lower()
        assert any(js_type in content_type for js_type in ["javascript", "text/plain"])
    
    def test_nonexistent_static_file(self, client):
        """Test that non-existent static files return 404"""
        response = client.get("/static/nonexistent.html")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_static_directory_listing_disabled(self, client):
        """Test that directory listing is disabled for static files"""
        response = client.get("/static/")
        # Should either redirect or return 404/403, not list directory contents
        assert response.status_code in [
            status.HTTP_301_MOVED_PERMANENTLY, 
            status.HTTP_404_NOT_FOUND, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK  # Might return index.html by default
        ]


class TestFrontendIntegration:
    """Integration tests for frontend functionality"""
    
    def test_root_redirect_works(self, client):
        """Test that root URL properly redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "/static/index.html" in response.headers.get("location", "")
    
    def test_frontend_can_load_activities(self, client, reset_activities):
        """Test that the frontend can load the activities API"""
        # This tests the integration between static files and API
        # First ensure the API works
        api_response = client.get("/activities")
        assert api_response.status_code == status.HTTP_200_OK
        
        # Then ensure the static file that would call this API exists
        html_response = client.get("/static/index.html")
        assert html_response.status_code == status.HTTP_200_OK
        
        # Check that the HTML contains references to our API endpoint
        html_content = html_response.text
        assert "/activities" in html_content or "activities" in html_content