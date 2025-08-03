"""
Django admin configuration for the news app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import NewsSource, Article, SearchLog, ArticleView


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    """Admin interface for NewsSource model."""
    list_display = [
        'name', 
        'domain', 
        'is_active', 
        'scraping_frequency', 
        'last_scraped_at', 
        'articles_count',
        'created_at'
    ]
    list_filter = ['is_active', 'scraping_frequency', 'created_at', 'last_scraped_at']
    search_fields = ['name', 'domain', 'base_url']
    readonly_fields = ['created_at', 'updated_at', 'last_scraped_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'domain', 'base_url')
        }),
        ('Scraping Configuration', {
            'fields': ('scraping_frequency', 'is_active', 'last_scraped_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def articles_count(self, obj):
        """Display article count for the source."""
        count = obj.get_articles_count()
        if count > 0:
            url = reverse('admin:news_article_changelist') + f'?source__id__exact={obj.id}'
            return format_html('<a href="{}">{} articles</a>', url, count)
        return '0 articles'
    articles_count.short_description = 'Articles'
    
    def get_queryset(self, request):
        """Optimize queryset with article count."""
        return super().get_queryset(request).prefetch_related('articles')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model."""
    list_display = [
        'title', 
        'source', 
        'published_at', 
        'word_count', 
        'reading_time',
        'view_count',
        'is_active',
        'has_summary'
    ]
    list_filter = [
        'source', 
        'is_active', 
        'published_at', 
        'created_at',
        'word_count'
    ]
    search_fields = ['title', 'description', 'content', 'url']
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'last_scraped_at',
        'word_count',
        'reading_time',
        'view_count'
    ]
    ordering = ['-published_at']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'description', 'content', 'url', 'published_at')
        }),
        ('Source & Status', {
            'fields': ('source', 'is_active')
        }),
        ('AI Summary', {
            'fields': ('summary',),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('word_count', 'reading_time', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_scraped_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_summary(self, obj):
        """Display if article has AI summary."""
        if obj.summary:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_summary.short_description = 'Summary'
    has_summary.boolean = True
    
    def view_count(self, obj):
        """Display view count for the article."""
        count = obj.get_view_count()
        if count > 0:
            url = reverse('admin:news_articleview_changelist') + f'?article__id__exact={obj.id}'
            return format_html('<a href="{}">{} views</a>', url, count)
        return '0 views'
    view_count.short_description = 'Views'
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('source').prefetch_related('views')
    
    actions = ['generate_summaries', 'mark_as_active', 'mark_as_inactive']
    
    def generate_summaries(self, request, queryset):
        """Action to generate summaries for selected articles."""
        count = 0
        for article in queryset:
            if not article.summary:
                # This would integrate with AI service
                article.summary = f"AI summary for: {article.title}"
                article.save()
                count += 1
        
        self.message_user(
            request, 
            f'Successfully generated summaries for {count} articles.'
        )
    generate_summaries.short_description = "Generate AI summaries for selected articles"
    
    def mark_as_active(self, request, queryset):
        """Action to mark articles as active."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully marked {updated} articles as active.')
    mark_as_active.short_description = "Mark selected articles as active"
    
    def mark_as_inactive(self, request, queryset):
        """Action to mark articles as inactive."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully marked {updated} articles as inactive.')
    mark_as_inactive.short_description = "Mark selected articles as inactive"


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    """Admin interface for SearchLog model."""
    list_display = [
        'query', 
        'result_count', 
        'execution_time', 
        'ip_address',
        'created_at'
    ]
    list_filter = ['created_at', 'result_count', 'execution_time']
    search_fields = ['query', 'ip_address', 'user_agent']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Search Information', {
            'fields': ('query', 'result_count', 'execution_time')
        }),
        ('User Information', {
            'fields': ('user_agent', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation of search logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of search logs."""
        return False


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    """Admin interface for ArticleView model."""
    list_display = [
        'article', 
        'view_type', 
        'ip_address',
        'session_id',
        'created_at'
    ]
    list_filter = ['view_type', 'created_at', 'article__source']
    search_fields = ['article__title', 'ip_address', 'session_id', 'user_agent']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('View Information', {
            'fields': ('article', 'view_type')
        }),
        ('User Information', {
            'fields': ('user_agent', 'ip_address', 'session_id')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation of article views."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of article views."""
        return False


# Customize admin site
admin.site.site_header = "Stock News Aggregator Admin"
admin.site.site_title = "Stock News Aggregator"
admin.site.index_title = "Welcome to Stock News Aggregator Administration" 