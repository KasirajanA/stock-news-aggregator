"""
Django management command to scrape news from configured sources.
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from news.models import NewsSource
from news.scrapers import scrape_all_sources, scrape_source


class Command(BaseCommand):
    help = 'Scrape news articles from configured sources'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Scrape only a specific source by name'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force scrape even if source was recently scraped'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be scraped without actually scraping'
        )
    
    def handle(self, *args, **options):
        source_name = options.get('source')
        force = options.get('force')
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual scraping will be performed')
            )
        
        if source_name:
            # Scrape specific source
            try:
                source = NewsSource.objects.get(name=source_name)
                self.scrape_single_source(source, force, dry_run)
            except NewsSource.DoesNotExist:
                raise CommandError(f'Source "{source_name}" not found')
        else:
            # Scrape all sources
            self.scrape_all_sources(force, dry_run)
    
    def scrape_single_source(self, source, force, dry_run):
        """Scrape a single news source."""
        self.stdout.write(f'Scraping source: {source.name}')
        
        if not source.is_active:
            self.stdout.write(
                self.style.WARNING(f'Source {source.name} is inactive, skipping')
            )
            return
        
        if not force and not source.should_scrape():
            self.stdout.write(
                self.style.WARNING(
                    f'Source {source.name} was recently scraped, skipping. Use --force to override.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Would scrape {source.name} from {source.base_url}')
            )
            return
        
        try:
            from news.scrapers import scrape_source
            count = scrape_source(source)
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully scraped {count} articles from {source.name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'No new articles found for {source.name}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error scraping {source.name}: {e}')
            )
    
    def scrape_all_sources(self, force, dry_run):
        """Scrape all active news sources."""
        sources = NewsSource.objects.filter(is_active=True)
        
        if not sources.exists():
            self.stdout.write(
                self.style.WARNING('No active news sources found')
            )
            return
        
        self.stdout.write(f'Found {sources.count()} active sources')
        
        if dry_run:
            for source in sources:
                self.stdout.write(
                    f'Would scrape: {source.name} ({source.base_url})'
                )
            return
        
        try:
            results = scrape_all_sources()
            
            total_articles = sum(results.values())
            
            if total_articles > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully scraped {total_articles} articles total'
                    )
                )
                
                for source_name, count in results.items():
                    if count > 0:
                        self.stdout.write(f'  {source_name}: {count} articles')
            else:
                self.stdout.write(
                    self.style.WARNING('No new articles found from any source')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during scraping: {e}')
            ) 