"""
Django management command to control the automatic scraping scheduler.
"""
from django.core.management.base import BaseCommand, CommandError
from news.services import start_automatic_scraping, stop_automatic_scraping, get_scraping_status


class Command(BaseCommand):
    help = 'Control the automatic scraping scheduler'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['start', 'stop', 'status'],
            help='Action to perform: start, stop, or status'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'start':
            self.start_scheduler()
        elif action == 'stop':
            self.stop_scheduler()
        elif action == 'status':
            self.show_status()
    
    def start_scheduler(self):
        """Start the automatic scraping scheduler."""
        try:
            start_automatic_scraping()
            self.stdout.write(
                self.style.SUCCESS('Automatic scraping scheduler started successfully')
            )
        except Exception as e:
            raise CommandError(f'Failed to start scheduler: {e}')
    
    def stop_scheduler(self):
        """Stop the automatic scraping scheduler."""
        try:
            stop_automatic_scraping()
            self.stdout.write(
                self.style.SUCCESS('Automatic scraping scheduler stopped successfully')
            )
        except Exception as e:
            raise CommandError(f'Failed to stop scheduler: {e}')
    
    def show_status(self):
        """Show the current scraping scheduler status."""
        try:
            status = get_scraping_status()
            
            self.stdout.write('=== Scraping Scheduler Status ===')
            self.stdout.write(f"Scheduler Running: {status['scheduler_running']}")
            self.stdout.write(f"Scraping Interval: {status['scraping_interval_seconds']} seconds")
            
            if status['last_scrape']:
                self.stdout.write(f"Last Scrape: {status['last_scrape']}")
            else:
                self.stdout.write("Last Scrape: Never")
            
            if status['next_scheduled_scrape']:
                self.stdout.write(f"Next Scheduled Scrape: {status['next_scheduled_scrape']}")
            else:
                self.stdout.write("Next Scheduled Scrape: Not scheduled")
            
            self.stdout.write('================================')
            
        except Exception as e:
            raise CommandError(f'Failed to get status: {e}') 