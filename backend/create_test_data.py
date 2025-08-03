#!/usr/bin/env python
"""
Script to create test data for the Stock News Aggregator.
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
django.setup()

from news.models import NewsSource, Article
from news.scrapers import scrape_source


def create_news_sources():
    """Create news sources as specified in the PRD."""
    sources_data = [
        {
            'name': 'LiveMint',
            'domain': 'livemint.com',
            'base_url': 'https://www.livemint.com',
            'scraping_frequency': 300,  # 5 minutes
            'is_active': True,
        },
        {
            'name': 'Economic Times',
            'domain': 'economictimes.indiatimes.com',
            'base_url': 'https://economictimes.indiatimes.com',
            'scraping_frequency': 300,
            'is_active': True,
        },
        {
            'name': 'MoneyControl',
            'domain': 'moneycontrol.com',
            'base_url': 'https://www.moneycontrol.com',
            'scraping_frequency': 300,
            'is_active': True,
        },
        {
            'name': 'Business Today',
            'domain': 'businesstoday.in',
            'base_url': 'https://www.businesstoday.in',
            'scraping_frequency': 300,
            'is_active': True,
        },
        {
            'name': 'Business Line',
            'domain': 'thehindubusinessline.com',
            'base_url': 'https://www.thehindubusinessline.com',
            'scraping_frequency': 300,
            'is_active': True,
        },
        {
            'name': 'Business Standard',
            'domain': 'business-standard.com',
            'base_url': 'https://www.business-standard.com',
            'scraping_frequency': 300,
            'is_active': True,
        },
        {
            'name': 'India Today',
            'domain': 'indiatoday.in',
            'base_url': 'https://www.indiatoday.in',
            'scraping_frequency': 300,
            'is_active': True,
        },
    ]
    
    print("Creating news sources...")
    for source_data in sources_data:
        source, created = NewsSource.objects.get_or_create(
            domain=source_data['domain'],
            defaults=source_data
        )
        if created:
            print(f"✅ Created source: {source.name}")
        else:
            print(f"ℹ️  Source already exists: {source.name}")
    
    print(f"\nTotal sources: {NewsSource.objects.count()}")


def create_sample_articles():
    """Create sample articles for testing."""
    print("\nCreating sample articles...")
    
    # Get sources
    sources = NewsSource.objects.all()
    
    sample_articles = [
        {
            'title': 'NIFTY 50 reaches new all-time high',
            'description': 'The NIFTY 50 index has reached a new all-time high, driven by strong corporate earnings.',
            'content': 'The NIFTY 50 index has reached a new all-time high, driven by strong corporate earnings and positive market sentiment. Analysts expect the rally to continue as companies report better-than-expected quarterly results.',
            'source': sources[0],  # LiveMint
            'url': 'https://www.livemint.com/markets/stock-market-news/nifty-50-reaches-new-all-time-high',
            'published_at': timezone.now() - timedelta(days=1),
        },
        {
            'title': 'SENSEX gains 500 points on positive global cues',
            'description': 'The BSE SENSEX gained 500 points following positive global market cues and strong domestic fundamentals.',
            'content': 'The BSE SENSEX gained 500 points following positive global market cues and strong domestic fundamentals. The rally was led by banking and IT stocks.',
            'source': sources[1],  # Economic Times
            'url': 'https://economictimes.indiatimes.com/markets/stocks/news/sensex-gains-500-points',
            'published_at': timezone.now() - timedelta(days=2),
        },
        {
            'title': 'RBI maintains repo rate at 6.5%',
            'description': 'The Reserve Bank of India has maintained the repo rate at 6.5% in its latest monetary policy review.',
            'content': 'The Reserve Bank of India has maintained the repo rate at 6.5% in its latest monetary policy review. The central bank cited inflation concerns and global economic uncertainty as reasons for the decision.',
            'source': sources[2],  # MoneyControl
            'url': 'https://www.moneycontrol.com/news/business/rbi-maintains-repo-rate-at-6-5',
            'published_at': timezone.now() - timedelta(days=3),
        },
    ]
    
    for article_data in sample_articles:
        article, created = Article.objects.get_or_create(
            url=article_data['url'],
            defaults=article_data
        )
        if created:
            print(f"✅ Created article: {article.title}")
        else:
            print(f"ℹ️  Article already exists: {article.title}")
    
    print(f"\nTotal articles: {Article.objects.count()}")


def test_scraping():
    """Test scraping functionality."""
    print("\nTesting scraping functionality...")
    
    sources = NewsSource.objects.filter(is_active=True)
    
    for source in sources:
        print(f"\nTesting scraping for {source.name}...")
        try:
            count = scrape_source(source)
            print(f"✅ Scraped {count} new articles from {source.name}")
        except Exception as e:
            print(f"❌ Error scraping {source.name}: {e}")


def main():
    """Main function to set up test data."""
    print("=== Stock News Aggregator - Test Data Setup ===\n")
    
    # Create news sources
    create_news_sources()
    
    # Create sample articles
    create_sample_articles()
    
    # Test scraping
    test_scraping()
    
    print("\n=== Setup Complete ===")
    print(f"Sources: {NewsSource.objects.count()}")
    print(f"Articles: {Article.objects.count()}")


if __name__ == '__main__':
    main() 