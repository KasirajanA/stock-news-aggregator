#!/usr/bin/env python
"""
Test script to verify all API endpoints are working correctly.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from news.models import NewsSource, Article, SearchLog, ArticleView


class APIEndpointTest(APITestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test source
        self.source = NewsSource.objects.create(
            name='Test Source',
            domain='test.com',
            base_url='https://test.com'
        )
        
        # Create test article
        self.article = Article.objects.create(
            url='https://test.com/article1',
            title='Test Article',
            description='Test description',
            content='Test content for the article.',
            published_at=datetime.now(),
            source=self.source
        )
    
    def test_news_list_endpoint(self):
        """Test GET /api/v1/news/ endpoint."""
        url = '/api/v1/news/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
    
    def test_news_detail_endpoint(self):
        """Test GET /api/v1/news/{id}/ endpoint."""
        url = f'/api/v1/news/{self.article.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')
    
    def test_news_summary_endpoint(self):
        """Test GET /api/v1/news/{id}/summary/ endpoint."""
        url = f'/api/v1/news/{self.article.id}/summary/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('is_cached', response.data)
        self.assertIn('processing_time', response.data)
    
    def test_sources_endpoint(self):
        """Test GET /api/v1/sources/ endpoint."""
        url = '/api/v1/sources/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_search_endpoint(self):
        """Test GET /api/v1/search/ endpoint."""
        url = '/api/v1/search/'
        response = self.client.get(url, {'query': 'test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('query', response.data)
    
    def test_health_check_endpoint(self):
        """Test GET /api/v1/health/ endpoint."""
        url = '/api/v1/health/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)


def test_with_real_data():
    """Test API endpoints with real data."""
    print("Testing API endpoints with real data...")
    
    # Check if we have test data
    article_count = Article.objects.count()
    source_count = NewsSource.objects.count()
    
    print(f"Found {article_count} articles and {source_count} sources")
    
    if article_count == 0:
        print("No test data found. Please run create_test_data.py first.")
        return False
    
    # Test each endpoint
    endpoints = [
        '/api/v1/news/',
        '/api/v1/sources/',
        '/api/v1/health/',
    ]
    
    client = Client()
    
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Test search endpoint
    try:
        response = client.get('/api/v1/search/', {'query': 'NIFTY'})
        if response.status_code == 200:
            print("✅ /api/v1/search/ - OK")
        else:
            print(f"❌ /api/v1/search/ - Status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/v1/search/ - Error: {e}")
    
    # Test article detail endpoint
    try:
        article = Article.objects.first()
        if article:
            response = client.get(f'/api/v1/news/{article.id}/')
            if response.status_code == 200:
                print(f"✅ /api/v1/news/{article.id}/ - OK")
            else:
                print(f"❌ /api/v1/news/{article.id}/ - Status {response.status_code}")
        else:
            print("❌ No articles found for detail test")
    except Exception as e:
        print(f"❌ Article detail test - Error: {e}")
    
    # Test summary endpoint
    try:
        article = Article.objects.first()
        if article:
            response = client.get(f'/api/v1/news/{article.id}/summary/')
            if response.status_code == 200:
                print(f"✅ /api/v1/news/{article.id}/summary/ - OK")
            else:
                print(f"❌ /api/v1/news/{article.id}/summary/ - Status {response.status_code}")
        else:
            print("❌ No articles found for summary test")
    except Exception as e:
        print(f"❌ Summary test - Error: {e}")
    
    return True


def test_model_functionality():
    """Test model functionality."""
    print("\nTesting model functionality...")
    
    # Test NewsSource methods
    sources = NewsSource.objects.all()
    for source in sources[:3]:  # Test first 3 sources
        article_count = source.get_articles_count()
        should_scrape = source.should_scrape()
        print(f"Source '{source.name}': {article_count} articles, should scrape: {should_scrape}")
    
    # Test Article methods
    articles = Article.objects.all()
    for article in articles[:3]:  # Test first 3 articles
        view_count = article.get_view_count()
        popularity_score = article.get_popularity_score()
        print(f"Article '{article.title}': {view_count} views, popularity: {popularity_score:.2f}")
    
    # Test SearchLog creation
    search_log = SearchLog.objects.create(
        query='test query',
        result_count=5,
        execution_time=0.123
    )
    print(f"Created search log: {search_log}")
    
    # Test ArticleView creation
    if articles.exists():
        article = articles.first()
        view = ArticleView.objects.create(
            article=article,
            view_type='detail',
            user_agent='Test Browser',
            ip_address='127.0.0.1'
        )
        print(f"Created article view: {view}")


if __name__ == '__main__':
    print("Running API endpoint tests...")
    
    # Test with real data
    test_with_real_data()
    
    # Test model functionality
    test_model_functionality()
    
    print("\n✅ All tests completed!") 