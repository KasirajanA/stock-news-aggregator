#!/usr/bin/env python
"""
Test script to demonstrate the web scraping functionality.
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
django.setup()

from django.test import Client
from news.models import NewsSource, Article
from news.scrapers import scrape_source, scrape_all_sources


def test_scraping_functionality():
    """Test the scraping functionality."""
    print("Testing web scraping functionality...")
    
    # Check if we have sources configured
    sources = NewsSource.objects.filter(is_active=True)
    print(f"Found {sources.count()} active news sources:")
    
    for source in sources:
        print(f"  - {source.name} ({source.domain})")
        print(f"    Base URL: {source.base_url}")
        print(f"    Scraping frequency: {source.scraping_frequency} seconds")
        print(f"    Last scraped: {source.last_scraped_at or 'Never'}")
        print(f"    Articles count: {source.get_articles_count()}")
        print()
    
    if not sources.exists():
        print("No active sources found. Please run create_test_data.py first.")
        return
    
    # Test scraping a single source
    source = sources.first()
    print(f"Testing scraping for: {source.name}")
    
    try:
        # Test scraping (this will actually try to scrape the website)
        print("Attempting to scrape articles...")
        count = scrape_source(source)
        
        if count > 0:
            print(f"✅ Successfully scraped {count} articles from {source.name}")
            
            # Show the latest articles
            latest_articles = Article.objects.filter(source=source).order_by('-created_at')[:5]
            print(f"\nLatest articles from {source.name}:")
            for article in latest_articles:
                print(f"  - {article.title}")
                print(f"    URL: {article.url}")
                print(f"    Published: {article.published_at}")
                print(f"    Word count: {article.word_count}")
                print()
        else:
            print(f"⚠️  No new articles found for {source.name}")
            
    except Exception as e:
        print(f"❌ Error scraping {source.name}: {e}")
        print("This is expected if the website structure has changed or if there are network issues.")


def test_scraping_api():
    """Test the scraping API endpoint."""
    print("\nTesting scraping API endpoint...")
    
    client = Client()
    
    # Test scraping all sources
    try:
        response = client.post('/api/v1/scrape/', {
            # Don't send source parameter to scrape all sources
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API scraping successful: {data.get('message', 'Unknown')}")
            print(f"   Total articles: {data.get('total_articles', 0)}")
        else:
            print(f"❌ API scraping failed: {response.status_code}")
            print(f"   Response: {response.content}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")


def test_management_command():
    """Test the management command."""
    print("\nTesting management command...")
    
    import subprocess
    
    try:
        # Test dry run
        result = subprocess.run([
            'python', 'manage.py', 'scrape_news', '--dry-run'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Management command dry run successful")
            print("Output:")
            print(result.stdout)
        else:
            print(f"❌ Management command failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Management command test error: {e}")


def show_scraping_stats():
    """Show scraping statistics."""
    print("\nScraping Statistics:")
    
    total_articles = Article.objects.count()
    total_sources = NewsSource.objects.count()
    active_sources = NewsSource.objects.filter(is_active=True).count()
    
    print(f"Total articles in database: {total_articles}")
    print(f"Total sources configured: {total_sources}")
    print(f"Active sources: {active_sources}")
    
    # Articles by source
    print("\nArticles by source:")
    for source in NewsSource.objects.all():
        count = source.get_articles_count()
        print(f"  {source.name}: {count} articles")
    
    # Recent articles
    recent_articles = Article.objects.order_by('-created_at')[:5]
    if recent_articles.exists():
        print("\nMost recent articles:")
        for article in recent_articles:
            print(f"  - {article.title} ({article.source.name})")
            print(f"    Created: {article.created_at}")
            print(f"    URL: {article.url}")
            print()


if __name__ == '__main__':
    print("=== Web Scraping Functionality Test ===\n")
    
    # Show current stats
    show_scraping_stats()
    
    # Test scraping functionality
    test_scraping_functionality()
    
    # Test API endpoint
    test_scraping_api()
    
    # Test management command
    test_management_command()
    
    print("\n=== Test Complete ===")
    print("\nNote: Actual web scraping may fail if:")
    print("1. Website structure has changed")
    print("2. Network connectivity issues")
    print("3. Rate limiting by the target websites")
    print("4. Robots.txt restrictions")
    print("\nThe scraping framework is designed to handle these gracefully.") 