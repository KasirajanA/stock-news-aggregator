"""
Unit tests for Django project setup.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path


class TestProjectSetup(unittest.TestCase):
    """Test cases for Django project setup."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_dir = Path(__file__).parent.parent
        
    def test_manage_py_exists(self):
        """Test that manage.py exists and is executable."""
        manage_py = self.base_dir / 'manage.py'
        self.assertTrue(manage_py.exists(), "manage.py should exist")
        self.assertTrue(manage_py.is_file(), "manage.py should be a file")
        
        # Check file content
        with open(manage_py, 'r') as f:
            content = f.read()
            self.assertIn('DJANGO_SETTINGS_MODULE', content)
            self.assertIn('stock_news_aggregator.settings', content)
    
    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists with required dependencies."""
        requirements = self.base_dir / 'requirements.txt'
        self.assertTrue(requirements.exists(), "requirements.txt should exist")
        
        with open(requirements, 'r') as f:
            content = f.read()
            self.assertIn('Django==4.2.7', content)
            self.assertIn('djangorestframework==3.14.0', content)
            self.assertIn('django-cors-headers==4.3.1', content)
    
    def test_settings_py_configuration(self):
        """Test that settings.py has proper configuration."""
        settings = self.base_dir / 'stock_news_aggregator' / 'settings.py'
        self.assertTrue(settings.exists(), "settings.py should exist")
        
        with open(settings, 'r') as f:
            content = f.read()
            
            # Check required settings
            self.assertIn('DATABASES', content)
            self.assertIn('REST_FRAMEWORK', content)
            self.assertIn('CORS_ALLOWED_ORIGINS', content)
            self.assertIn('INSTALLED_APPS', content)
            
            # Check apps are included
            self.assertIn("'news'", content)
            self.assertIn("'market_data'", content)
            self.assertIn("'rest_framework'", content)
    
    def test_urls_py_configuration(self):
        """Test that main urls.py has proper configuration."""
        urls = self.base_dir / 'stock_news_aggregator' / 'urls.py'
        self.assertTrue(urls.exists(), "urls.py should exist")
        
        with open(urls, 'r') as f:
            content = f.read()
            self.assertIn('admin.site.urls', content)
            self.assertIn('include(\'news.urls\')', content)
            self.assertIn('include(\'market_data.urls\')', content)
    
    def test_app_structure(self):
        """Test that apps have proper structure."""
        apps = ['news', 'market_data']
        
        for app in apps:
            app_dir = self.base_dir / app
            self.assertTrue(app_dir.exists(), f"{app} directory should exist")
            self.assertTrue(app_dir.is_dir(), f"{app} should be a directory")
            
            # Check required files
            required_files = ['__init__.py', 'apps.py', 'views.py', 'urls.py']
            for file_name in required_files:
                file_path = app_dir / file_name
                self.assertTrue(file_path.exists(), f"{app}/{file_name} should exist")
    
    def test_news_app_urls(self):
        """Test that news app URLs are properly configured."""
        urls = self.base_dir / 'news' / 'urls.py'
        self.assertTrue(urls.exists(), "news/urls.py should exist")
        
        with open(urls, 'r') as f:
            content = f.read()
            self.assertIn('ArticleViewSet', content)
            self.assertIn('NewsSourceViewSet', content)
            self.assertIn('SearchView', content)
    
    def test_market_data_app_urls(self):
        """Test that market_data app URLs are properly configured."""
        urls = self.base_dir / 'market_data' / 'urls.py'
        self.assertTrue(urls.exists(), "market_data/urls.py should exist")
        
        with open(urls, 'r') as f:
            content = f.read()
            self.assertIn('MarketIndicesView', content)
            self.assertIn('HealthCheckView', content)
    
    def test_project_structure(self):
        """Test overall project structure."""
        required_dirs = [
            'stock_news_aggregator',
            'news',
            'market_data',
            'tests',
        ]
        
        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            self.assertTrue(dir_path.exists(), f"{dir_name} directory should exist")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} should be a directory")
    
    def test_wsgi_configuration(self):
        """Test that WSGI configuration is correct."""
        wsgi = self.base_dir / 'stock_news_aggregator' / 'wsgi.py'
        self.assertTrue(wsgi.exists(), "wsgi.py should exist")
        
        with open(wsgi, 'r') as f:
            content = f.read()
            self.assertIn('get_wsgi_application', content)
            self.assertIn('stock_news_aggregator.settings', content)
    
    def test_asgi_configuration(self):
        """Test that ASGI configuration is correct."""
        asgi = self.base_dir / 'stock_news_aggregator' / 'asgi.py'
        self.assertTrue(asgi.exists(), "asgi.py should exist")
        
        with open(asgi, 'r') as f:
            content = f.read()
            self.assertIn('get_asgi_application', content)
            self.assertIn('stock_news_aggregator.settings', content)


if __name__ == '__main__':
    unittest.main() 