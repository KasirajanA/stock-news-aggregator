"""
Services for automatic news scraping and scheduling.
"""
import logging
import threading
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .models import NewsSource
from .scrapers import scrape_all_sources, scrape_source

logger = logging.getLogger(__name__)


class ScrapingScheduler:
    """Manages automatic scraping with scheduling and on-demand triggers."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.scraping_interval = 15 * 60  # 15 minutes in seconds
        self.last_scrape_time = None
        self.cache_key = 'last_automatic_scrape'
    
    def start(self):
        """Start the automatic scraping scheduler."""
        if self.running:
            logger.info("Scraping scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Automatic scraping scheduler started")
    
    def stop(self):
        """Stop the automatic scraping scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Automatic scraping scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            try:
                # Check if it's time to scrape
                if self._should_scrape():
                    logger.info("Triggering automatic scraping...")
                    self._perform_scraping()
                
                # Sleep for 1 minute before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scraping scheduler: {e}")
                time.sleep(60)  # Continue running despite errors
    
    def _should_scrape(self):
        """Check if automatic scraping should be performed."""
        # Get last scrape time from cache
        last_scrape = cache.get(self.cache_key)
        
        if not last_scrape:
            # First time running, scrape immediately
            return True
        
        # Check if 15 minutes have passed since last scrape
        time_since_last = timezone.now() - last_scrape
        return time_since_last.total_seconds() >= self.scraping_interval
    
    def _perform_scraping(self):
        """Perform the actual scraping."""
        try:
            # Check if any sources need scraping
            sources_to_scrape = []
            for source in NewsSource.objects.filter(is_active=True):
                if source.should_scrape():
                    sources_to_scrape.append(source)
            
            if not sources_to_scrape:
                logger.info("No sources need scraping at this time")
                return
            
            # Perform scraping
            results = scrape_all_sources()
            total_articles = sum(results.values())
            
            # Update last scrape time
            cache.set(self.cache_key, timezone.now(), timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Automatic scraping completed: {total_articles} articles scraped")
            
        except Exception as e:
            logger.error(f"Error during automatic scraping: {e}")
    
    def trigger_on_demand(self):
        """Trigger scraping on demand (e.g., when news page is loaded)."""
        try:
            logger.info("Triggering on-demand scraping...")
            
            # Check if we should scrape (avoid too frequent scraping)
            last_scrape = cache.get(self.cache_key)
            if last_scrape:
                time_since_last = timezone.now() - last_scrape
                if time_since_last.total_seconds() < 300:  # 5 minutes minimum between scrapes
                    logger.info("Skipping on-demand scrape (too recent)")
                    return False
            
            # Perform scraping
            results = scrape_all_sources()
            total_articles = sum(results.values())
            
            # Update last scrape time
            cache.set(self.cache_key, timezone.now(), timeout=3600)
            
            logger.info(f"On-demand scraping completed: {total_articles} articles scraped")
            return True
            
        except Exception as e:
            logger.error(f"Error during on-demand scraping: {e}")
            return False
    
    def get_scraping_status(self):
        """Get current scraping status."""
        last_scrape = cache.get(self.cache_key)
        next_scrape = None
        
        if last_scrape:
            next_scrape = last_scrape + timedelta(seconds=self.scraping_interval)
        
        return {
            'scheduler_running': self.running,
            'last_scrape': last_scrape,
            'next_scheduled_scrape': next_scrape,
            'scraping_interval_seconds': self.scraping_interval
        }


# Global scheduler instance
scraping_scheduler = ScrapingScheduler()


def start_automatic_scraping():
    """Start the automatic scraping scheduler."""
    scraping_scheduler.start()


def stop_automatic_scraping():
    """Stop the automatic scraping scheduler."""
    scraping_scheduler.stop()


def trigger_scraping_on_demand():
    """Trigger scraping on demand (called when news page is loaded)."""
    return scraping_scheduler.trigger_on_demand()


def get_scraping_status():
    """Get current scraping status."""
    return scraping_scheduler.get_scraping_status()


class ScrapingService:
    """Service class for scraping operations."""
    
    @staticmethod
    def scrape_all_sources_with_status():
        """Scrape all sources and return detailed status."""
        try:
            start_time = timezone.now()
            results = scrape_all_sources()
            end_time = timezone.now()
            
            total_articles = sum(results.values())
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'results': results,
                'total_articles': total_articles,
                'processing_time': round(processing_time, 2),
                'timestamp': start_time,
                'sources_scraped': len([r for r in results.values() if r > 0])
            }
            
        except Exception as e:
            logger.error(f"Error in scraping service: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timezone.now()
            }
    
    @staticmethod
    def scrape_single_source_with_status(source_name):
        """Scrape a single source and return detailed status."""
        try:
            source = NewsSource.objects.get(name=source_name)
            start_time = timezone.now()
            count = scrape_source(source)
            end_time = timezone.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'source': source.name,
                'articles_scraped': count,
                'processing_time': round(processing_time, 2),
                'timestamp': start_time
            }
            
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f'Source "{source_name}" not found'
            }
        except Exception as e:
            logger.error(f"Error scraping source {source_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_sources_status():
        """Get status of all news sources."""
        sources = NewsSource.objects.all()
        status_list = []
        
        for source in sources:
            last_scraped = source.last_scraped_at
            time_since_last = None
            should_scrape = False
            
            if last_scraped:
                time_since_last = timezone.now() - last_scraped
                should_scrape = source.should_scrape()
            
            status_list.append({
                'id': source.id,
                'name': source.name,
                'domain': source.domain,
                'is_active': source.is_active,
                'articles_count': source.get_articles_count(),
                'last_scraped_at': last_scraped,
                'time_since_last': time_since_last.total_seconds() if time_since_last else None,
                'should_scrape': should_scrape,
                'scraping_frequency': source.scraping_frequency
            })
        
        return status_list 