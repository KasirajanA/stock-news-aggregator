#!/usr/bin/env python
"""
Script to reset scraping timestamps for testing automatic scraping.
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_news_aggregator.settings')
django.setup()

from news.models import NewsSource


def reset_scraping_timestamps():
    """Reset last_scraped_at timestamps to force scraping."""
    print("=== Resetting Scraping Timestamps ===\n")
    
    # Get all sources
    sources = NewsSource.objects.all()
    
    for source in sources:
        print(f"Source: {source.name}")
        print(f"  Current last_scraped_at: {source.last_scraped_at}")
        print(f"  Current scraping_frequency: {source.scraping_frequency} seconds")
        print(f"  Should scrape: {source.should_scrape()}")
        
        # Reset to 2 hours ago to force scraping
        old_time = timezone.now() - timedelta(hours=2)
        source.last_scraped_at = old_time
        source.save()
        
        print(f"  Reset to: {source.last_scraped_at}")
        print(f"  Should scrape now: {source.should_scrape()}")
        print()
    
    print("✅ All scraping timestamps reset successfully!")
    print("\nNow you can test automatic scraping and it should find new articles.")


def update_scraping_frequency():
    """Update scraping frequency to be more aggressive for testing."""
    print("=== Updating Scraping Frequency ===\n")
    
    # Set all sources to scrape every 5 minutes for testing
    sources = NewsSource.objects.all()
    
    for source in sources:
        print(f"Source: {source.name}")
        print(f"  Old frequency: {source.scraping_frequency} seconds")
        
        # Set to 5 minutes (300 seconds)
        source.scraping_frequency = 300
        source.save()
        
        print(f"  New frequency: {source.scraping_frequency} seconds")
        print()
    
    print("✅ All scraping frequencies updated to 5 minutes!")


def show_current_status():
    """Show current scraping status."""
    print("=== Current Scraping Status ===\n")
    
    sources = NewsSource.objects.all()
    
    for source in sources:
        print(f"Source: {source.name}")
        print(f"  Domain: {source.domain}")
        print(f"  Active: {source.is_active}")
        print(f"  Articles: {source.get_articles_count()}")
        print(f"  Last scraped: {source.last_scraped_at}")
        print(f"  Frequency: {source.scraping_frequency} seconds")
        print(f"  Should scrape: {source.should_scrape()}")
        print()


if __name__ == '__main__':
    print("=== Scraping Timestamp Reset Tool ===\n")
    
    # Show current status
    show_current_status()
    print()
    
    # Ask user what to do
    print("Options:")
    print("1. Reset timestamps (force scraping)")
    print("2. Update frequency (5 minutes)")
    print("3. Both")
    print("4. Show status only")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        reset_scraping_timestamps()
    elif choice == '2':
        update_scraping_frequency()
    elif choice == '3':
        reset_scraping_timestamps()
        print()
        update_scraping_frequency()
    elif choice == '4':
        pass  # Already shown above
    else:
        print("Invalid choice. Showing status only.")
    
    print("\n=== Final Status ===")
    show_current_status() 