"""
Django REST Framework serializers for the news app.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import NewsSource, Article, SearchLog, ArticleView


class NewsSourceSerializer(serializers.ModelSerializer):
    """Serializer for NewsSource model."""
    articles_count = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsSource
        fields = [
            'id', 'name', 'domain', 'base_url', 'scraping_frequency',
            'is_active', 'last_scraped_at', 'articles_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_scraped_at']


class NewsSourceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for NewsSource list view."""
    articles_count = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsSource
        fields = ['id', 'name', 'domain', 'is_active', 'articles_count']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model."""
    source = NewsSourceListSerializer(read_only=True)
    view_count = serializers.ReadOnlyField()
    has_summary = serializers.ReadOnlyField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'url', 'title', 'description', 'summary', 'content',
            'published_at', 'source', 'is_active', 'word_count',
            'reading_time', 'view_count', 'has_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_scraped_at',
            'word_count', 'reading_time', 'view_count'
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Article list view."""
    source = NewsSourceListSerializer(read_only=True)
    view_count = serializers.ReadOnlyField()
    has_summary = serializers.ReadOnlyField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'description', 'summary', 'published_at',
            'source', 'word_count', 'reading_time', 'view_count',
            'has_summary', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'word_count', 'reading_time',
            'view_count', 'has_summary'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Article detail view."""
    source = NewsSourceSerializer(read_only=True)
    view_count = serializers.ReadOnlyField()
    has_summary = serializers.ReadOnlyField()
    summary_generated_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'url', 'title', 'description', 'summary', 'content',
            'published_at', 'source', 'is_active', 'word_count',
            'reading_time', 'view_count', 'has_summary',
            'summary_generated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_scraped_at',
            'word_count', 'reading_time', 'view_count', 'has_summary'
        ]
    
    def get_summary_generated_at(self, obj):
        """Get the timestamp when summary was generated."""
        if obj.summary:
            return obj.updated_at
        return None


class ArticleSummarySerializer(serializers.ModelSerializer):
    """Serializer for article summary endpoint."""
    summary = serializers.CharField(read_only=True)
    is_cached = serializers.BooleanField(read_only=True)
    processing_time = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'is_cached', 'processing_time']


class SearchLogSerializer(serializers.ModelSerializer):
    """Serializer for SearchLog model."""
    
    class Meta:
        model = SearchLog
        fields = [
            'id', 'query', 'result_count', 'execution_time',
            'user_agent', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ArticleViewSerializer(serializers.ModelSerializer):
    """Serializer for ArticleView model."""
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = ArticleView
        fields = [
            'id', 'article', 'article_title', 'view_type',
            'user_agent', 'ip_address', 'session_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SearchRequestSerializer(serializers.Serializer):
    """Serializer for search request validation."""
    query = serializers.CharField(max_length=500, required=True)
    source = serializers.IntegerField(required=False, allow_null=True)
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)
    
    def validate(self, data):
        """Validate search parameters."""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "date_from cannot be later than date_to"
            )
        
        return data 