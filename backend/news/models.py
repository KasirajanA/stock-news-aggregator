"""
Models for the news app.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class NewsSource(models.Model):
    """Model for news sources."""
    name = models.CharField(max_length=100, unique=True, help_text="Source name (e.g., 'LiveMint')")
    domain = models.CharField(max_length=255, unique=True, help_text="Source domain")
    base_url = models.CharField(max_length=500, help_text="Base URL for scraping")
    scraping_frequency = models.IntegerField(
        default=3600,  # 1 hour in seconds
        validators=[MinValueValidator(300), MaxValueValidator(86400)],  # 5 min to 24 hours
        help_text="Scraping interval in seconds"
    )
    is_active = models.BooleanField(default=True, help_text="Whether source is active")
    last_scraped_at = models.DateTimeField(null=True, blank=True, help_text="Last successful scraping")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_sources'
        verbose_name = 'News Source'
        verbose_name_plural = 'News Sources'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['last_scraped_at']),
        ]
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_articles_count(self):
        """Get the number of articles from this source."""
        return self.articles.filter(is_active=True).count()

    def should_scrape(self):
        """Check if source should be scraped based on frequency."""
        if not self.last_scraped_at:
            return True
        time_since_last = timezone.now() - self.last_scraped_at
        return time_since_last.total_seconds() >= self.scraping_frequency


class Article(models.Model):
    """Model for news articles."""
    url = models.CharField(max_length=2048, unique=True, help_text="Original article URL")
    title = models.CharField(max_length=500, help_text="Article headline")
    description = models.TextField(help_text="Article summary/description")
    summary = models.TextField(
        null=True, 
        blank=True, 
        help_text="AI-generated summary (stored after first generation)"
    )
    content = models.TextField(help_text="Full article content")
    published_at = models.DateTimeField(help_text="Original publication date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped_at = models.DateTimeField(auto_now_add=True, help_text="Last scraping timestamp")
    source = models.ForeignKey(
        NewsSource, 
        on_delete=models.CASCADE, 
        related_name='articles',
        help_text="Reference to news source"
    )
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")
    word_count = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Article word count for analytics"
    )
    reading_time = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Estimated reading time in minutes"
    )

    class Meta:
        db_table = 'articles'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        indexes = [
            models.Index(fields=['published_at']),
            models.Index(fields=['source']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['title', 'description']),  # For basic search
        ]
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to calculate word count and reading time."""
        if not self.word_count:
            self.word_count = len(self.content.split())
        if not self.reading_time:
            # Average reading speed: 200-250 words per minute
            self.reading_time = max(1, self.word_count // 200)
        super().save(*args, **kwargs)

    def get_view_count(self):
        """Get the total number of views for this article."""
        return self.views.count()

    def get_popularity_score(self):
        """Calculate popularity score based on views."""
        view_count = self.get_view_count()
        days_since_published = (timezone.now() - self.published_at).days
        if days_since_published == 0:
            days_since_published = 1
        return view_count / days_since_published


class SearchLog(models.Model):
    """Model for tracking search queries."""
    query = models.CharField(max_length=500, help_text="Search query text")
    result_count = models.IntegerField(help_text="Number of results returned")
    execution_time = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        null=True, 
        blank=True,
        help_text="Query execution time in seconds"
    )
    user_agent = models.CharField(
        max_length=500, 
        null=True, 
        blank=True,
        help_text="User agent string"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="User IP address"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_logs'
        verbose_name = 'Search Log'
        verbose_name_plural = 'Search Logs'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['execution_time']),
            models.Index(fields=['query']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.query} ({self.result_count} results)"


class ArticleView(models.Model):
    """Model for tracking article view statistics."""
    VIEW_TYPES = [
        ('list', 'List View'),
        ('detail', 'Detail View'),
        ('summary', 'Summary View'),
    ]
    
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='views',
        help_text="Reference to article"
    )
    view_type = models.CharField(
        max_length=10, 
        choices=VIEW_TYPES,
        help_text="Type of view"
    )
    user_agent = models.CharField(
        max_length=500, 
        null=True, 
        blank=True,
        help_text="User agent string"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="User IP address"
    )
    session_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Session identifier"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_views'
        verbose_name = 'Article View'
        verbose_name_plural = 'Article Views'
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['created_at']),
            models.Index(fields=['view_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article.title} - {self.view_type}" 