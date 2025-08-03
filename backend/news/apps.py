from django.apps import AppConfig
import threading

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'News Management'
    
    def ready(self):
        """Start automatic scraping scheduler when Django is ready."""
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            # Only start scheduler in the main process, not in reloader
            try:
                from .services import start_automatic_scraping
                # Start scraping scheduler in background thread
                threading.Thread(target=start_automatic_scraping, daemon=True).start()
            except Exception as e:
                # Log error but don't prevent app from starting
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to start automatic scraping: {e}") 