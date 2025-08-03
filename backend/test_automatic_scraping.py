#!/usr/bin/env python
"""
Test script to demonstrate the automatic scraping functionality.
"""
import os
import sys
import django
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
django.setup()

from django.test import Client
from news.models import NewsSource, Article
from news.services import (
    start_automatic_scraping, 
    stop_automatic_scraping, 
    get_scraping_status,
    trigger_scraping_on_demand,
    ScrapingService
)


def test_automatic_scraping_system():
    """Test the automatic scraping system."""
    print("=== Testing Automatic Scraping System ===\n")
    
    # Test 1: Check initial status
    print("1. Checking initial scraping status...")
    status = get_scraping_status()
    print(f"   Scheduler Running: {status['scheduler_running']}")
    print(f"   Last Scrape: {status['last_scrape']}")
    print(f"   Next Scheduled: {status['next_scheduled_scrape']}")
    print()
    
    # Test 2: Start automatic scraping
    print("2. Starting automatic scraping scheduler...")
    start_automatic_scraping()
    time.sleep(2)  # Wait for scheduler to start
    
    status = get_scraping_status()
    print(f"   Scheduler Running: {status['scheduler_running']}")
    print()
    
    # Test 3: Test on-demand scraping trigger
    print("3. Testing on-demand scraping trigger...")
    result = trigger_scraping_on_demand()
    print(f"   On-demand scraping triggered: {result}")
    print()
    
    # Test 4: Test API endpoints
    print("4. Testing API endpoints...")
    client = Client()
    
    # Test scraping status endpoint
    try:
        response = client.get('/api/v1/scraping-status/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Scraping status API working")
            print(f"   Sources configured: {len(data.get('sources_status', []))}")
        else:
            print(f"   ❌ Scraping status API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Scraping status API error: {e}")
    
    # Test manual scraping endpoint
    try:
        response = client.post('/api/v1/scrape/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Manual scraping API working")
            print(f"   Articles scraped: {data.get('total_articles', 0)}")
        else:
            print(f"   ❌ Manual scraping API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Manual scraping API error: {e}")
    
    print()
    
    # Test 5: Test news list endpoint (triggers on-demand scraping)
    print("5. Testing news list endpoint (should trigger on-demand scraping)...")
    try:
        response = client.get('/api/v1/news/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ News list API working")
            print(f"   Articles returned: {len(data.get('results', []))}")
            print(f"   Total articles: {data.get('count', 0)}")
        else:
            print(f"   ❌ News list API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ News list API error: {e}")
    
    print()
    
    # Test 6: Show sources status
    print("6. Sources status:")
    sources_status = ScrapingService.get_sources_status()
    for source in sources_status:
        print(f"   {source['name']}: {source['articles_count']} articles")
        print(f"     Last scraped: {source['last_scraped_at']}")
        print(f"     Should scrape: {source['should_scrape']}")
        print()
    
    # Test 7: Stop automatic scraping
    print("7. Stopping automatic scraping scheduler...")
    stop_automatic_scraping()
    time.sleep(2)
    
    status = get_scraping_status()
    print(f"   Scheduler Running: {status['scheduler_running']}")
    print()


def test_scheduler_control():
    """Test scheduler control via management commands."""
    print("=== Testing Scheduler Control ===\n")
    
    import subprocess
    
    # Test status command
    try:
        result = subprocess.run([
            'python', 'manage.py', 'control_scraping', 'status'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Status command working:")
            print(result.stdout)
        else:
            print(f"❌ Status command failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Status command error: {e}")
    
    print()


def show_automatic_scraping_features():
    """Show the automatic scraping features."""
    print("=== Automatic Scraping Features ===\n")
    
    features = [
        "🔄 **Every 15 Minutes**: Automatic scraping runs every 15 minutes",
        "📱 **On-Demand**: Scraping triggered when news list page is loaded",
        "⏱️ **Smart Timing**: Avoids too frequent scraping (5-minute minimum between on-demand scrapes)",
        "🛡️ **Error Handling**: Graceful handling of network issues and parsing failures",
        "📊 **Status Monitoring**: Real-time status of scraping scheduler and sources",
        "🎛️ **Manual Control**: Start/stop scheduler via API or management commands",
        "📈 **Background Processing**: Scraping runs in background threads",
        "💾 **Caching**: Last scrape time cached to avoid redundant operations",
        "🔍 **Source Monitoring**: Track which sources need scraping",
        "📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n=== Usage Examples ===\n")
    
    examples = [
        "**API Endpoints:**",
        "  GET /api/v1/news/ - Triggers on-demand scraping",
        "  GET /api/v1/scraping-status/ - Get scraping status",
        "  POST /api/v1/scraping-status/ - Control scheduler (start/stop)",
        "  POST /api/v1/scrape/ - Manual scraping",
        "",
        "**Management Commands:**",
        "  python manage.py control_scraping status",
        "  python manage.py control_scraping start",
        "  python manage.py control_scraping stop",
        "",
        "**Programmatic:**",
        "  from news.services import start_automatic_scraping",
        "  from news.services import trigger_scraping_on_demand",
        "  from news.services import get_scraping_status"
    ]
    
    for example in examples:
        print(f"   {example}")


if __name__ == '__main__':
    print("=== Automatic Scraping System Test ===\n")
    
    # Show features
    show_automatic_scraping_features()
    print()
    
    # Test the system
    test_automatic_scraping_system()
    
    # Test scheduler control
    test_scheduler_control()
    
    print("=== Test Complete ===")
    print("\nThe automatic scraping system is now configured to:")
    print("1. Run every 15 minutes automatically")
    print("2. Trigger when the news list page is loaded")
    print("3. Provide status monitoring and manual control")
    print("4. Handle errors gracefully and log all activities") 