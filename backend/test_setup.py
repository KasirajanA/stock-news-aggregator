#!/usr/bin/env python
"""
Basic test script to verify Django project setup.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def test_django_setup():
    """Test that Django is properly configured."""
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
        django.setup()
        
        print("✅ Django setup successful")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Test settings
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ Installed apps: {len(settings.INSTALLED_APPS)} apps")
        
        return True
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False


if __name__ == '__main__':
    success = test_django_setup()
    sys.exit(0 if success else 1) 