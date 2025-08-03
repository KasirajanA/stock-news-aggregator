#!/usr/bin/env python
"""
Test script to verify project structure and files exist.
"""
import os
import sys
from pathlib import Path


def test_project_structure():
    """Test that all required files and directories exist."""
    base_dir = Path(__file__).parent
    
    required_files = [
        'manage.py',
        'requirements.txt',
        'stock_news_aggregator/__init__.py',
        'stock_news_aggregator/settings.py',
        'stock_news_aggregator/urls.py',
        'stock_news_aggregator/wsgi.py',
        'stock_news_aggregator/asgi.py',
        'news/__init__.py',
        'news/apps.py',
        'news/models.py',
        'news/views.py',
        'news/urls.py',
        'market_data/__init__.py',
        'market_data/apps.py',
        'market_data/views.py',
        'market_data/urls.py',
    ]
    
    required_dirs = [
        'stock_news_aggregator',
        'news',
        'market_data',
    ]
    
    print("Testing project structure...")
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ Directory exists: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
            return False
    
    # Check files
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists() and file_path.is_file():
            print(f"✅ File exists: {file_name}")
        else:
            print(f"❌ File missing: {file_name}")
            return False
    
    # Check requirements.txt content
    requirements_path = base_dir / 'requirements.txt'
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            content = f.read()
            if 'Django==' in content and 'djangorestframework==' in content:
                print("✅ requirements.txt contains required dependencies")
            else:
                print("❌ requirements.txt missing required dependencies")
                return False
    
    # Check settings.py content
    settings_path = base_dir / 'stock_news_aggregator' / 'settings.py'
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            content = f.read()
            if 'DATABASES' in content and 'REST_FRAMEWORK' in content:
                print("✅ settings.py contains required configuration")
            else:
                print("❌ settings.py missing required configuration")
                return False
    
    print("\n🎉 All project structure tests passed!")
    return True


if __name__ == '__main__':
    success = test_project_structure()
    sys.exit(0 if success else 1) 