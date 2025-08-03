"""
Unit tests for Django models.
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from news.models import NewsSource, Article, SearchLog, ArticleView


class NewsSourceModelTest(TestCase):
    """Test cases for NewsSource model."""
    
    def setUp(self):
        """Set up test data."""
        self.source = NewsSource.objects.create(
            name='Test Source',
            domain='test.com',
            base_url='https://test.com',
            scraping_frequency=3600
        )
    
    def test_news_source_creation(self):
        """Test that NewsSource can be created."""
        self.assertEqual(self.source.name, 'Test Source')
        self.assertEqual(self.source.domain, 'test.com')
        self.assertEqual(self.source.base_url, 'https://test.com')
        self.assertEqual(self.source.scraping_frequency, 3600)
        self.assertTrue(self.source.is_active)
    
    def test_news_source_str(self):
        """Test string representation."""
        self.assertEqual(str(self.source), 'Test Source')
    
    def test_news_source_unique_name(self):
        """Test that source name must be unique."""
        with self.assertRaises(IntegrityError):
            NewsSource.objects.create(
                name='Test Source',
                domain='other.com',
                base_url='https://other.com'
            )
    
    def test_news_source_unique_domain(self):
        """Test that source domain must be unique."""
        with self.assertRaises(IntegrityError):
            NewsSource.objects.create(
                name='Other Source',
                domain='test.com',
                base_url='https://other.com'
            )
    
    def test_news_source_get_articles_count(self):
        """Test get_articles_count method."""
        self.assertEqual(self.source.get_articles_count(), 0)
    
    def test_news_source_should_scrape(self):
        """Test should_scrape method."""
        # Should scrape if never scraped
        self.assertTrue(self.source.should_scrape())
        
        # Should not scrape if recently scraped
        self.source.last_scraped_at = timezone.now()
        self.source.save()
        self.assertFalse(self.source.should_scrape())
    
    def test_news_source_validation(self):
        """Test field validation."""
        # Test scraping_frequency validation
        with self.assertRaises(ValidationError):
            source = NewsSource(
                name='Invalid Source',
                domain='invalid.com',
                base_url='https://invalid.com',
                scraping_frequency=100  # Too low
            )
            source.full_clean()


class ArticleModelTest(TestCase):
    """Test cases for Article model."""
    
    def setUp(self):
        """Set up test data."""
        self.source = NewsSource.objects.create(
            name='Test Source',
            domain='test.com',
            base_url='https://test.com'
        )
        self.article = Article.objects.create(
            url='https://test.com/article1',
            title='Test Article',
            description='Test description',
            content='This is a test article content with multiple words.',
            published_at=timezone.now(),
            source=self.source
        )
    
    def test_article_creation(self):
        """Test that Article can be created."""
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.url, 'https://test.com/article1')
        self.assertEqual(self.article.source, self.source)
        self.assertTrue(self.article.is_active)
    
    def test_article_str(self):
        """Test string representation."""
        self.assertEqual(str(self.article), 'Test Article')
    
    def test_article_unique_url(self):
        """Test that article URL must be unique."""
        with self.assertRaises(IntegrityError):
            Article.objects.create(
                url='https://test.com/article1',
                title='Another Article',
                description='Another description',
                content='Another content',
                published_at=timezone.now(),
                source=self.source
            )
    
    def test_article_word_count_calculation(self):
        """Test automatic word count calculation."""
        self.assertEqual(self.article.word_count, 9)  # "This is a test article content with multiple words."
    
    def test_article_reading_time_calculation(self):
        """Test automatic reading time calculation."""
        # 9 words / 200 words per minute = 1 minute (minimum)
        self.assertEqual(self.article.reading_time, 1)
    
    def test_article_get_view_count(self):
        """Test get_view_count method."""
        self.assertEqual(self.article.get_view_count(), 0)
        
        # Create some views
        ArticleView.objects.create(
            article=self.article,
            view_type='detail'
        )
        ArticleView.objects.create(
            article=self.article,
            view_type='list'
        )
        
        self.assertEqual(self.article.get_view_count(), 2)
    
    def test_article_get_popularity_score(self):
        """Test get_popularity_score method."""
        # No views, should return 0
        self.assertEqual(self.article.get_popularity_score(), 0)
        
        # Add a view
        ArticleView.objects.create(
            article=self.article,
            view_type='detail'
        )
        
        # Should have some popularity score
        score = self.article.get_popularity_score()
        self.assertGreater(score, 0)


class SearchLogModelTest(TestCase):
    """Test cases for SearchLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.search_log = SearchLog.objects.create(
            query='test query',
            result_count=5,
            execution_time=0.123
        )
    
    def test_search_log_creation(self):
        """Test that SearchLog can be created."""
        self.assertEqual(self.search_log.query, 'test query')
        self.assertEqual(self.search_log.result_count, 5)
        self.assertEqual(float(self.search_log.execution_time), 0.123)
    
    def test_search_log_str(self):
        """Test string representation."""
        self.assertEqual(str(self.search_log), 'test query (5 results)')


class ArticleViewModelTest(TestCase):
    """Test cases for ArticleView model."""
    
    def setUp(self):
        """Set up test data."""
        self.source = NewsSource.objects.create(
            name='Test Source',
            domain='test.com',
            base_url='https://test.com'
        )
        self.article = Article.objects.create(
            url='https://test.com/article1',
            title='Test Article',
            description='Test description',
            content='Test content',
            published_at=timezone.now(),
            source=self.source
        )
        self.article_view = ArticleView.objects.create(
            article=self.article,
            view_type='detail',
            user_agent='Test Browser',
            ip_address='127.0.0.1'
        )
    
    def test_article_view_creation(self):
        """Test that ArticleView can be created."""
        self.assertEqual(self.article_view.article, self.article)
        self.assertEqual(self.article_view.view_type, 'detail')
        self.assertEqual(self.article_view.user_agent, 'Test Browser')
        self.assertEqual(self.article_view.ip_address, '127.0.0.1')
    
    def test_article_view_str(self):
        """Test string representation."""
        self.assertEqual(str(self.article_view), 'Test Article - detail')
    
    def test_article_view_choices(self):
        """Test view type choices."""
        choices = [choice[0] for choice in ArticleView.VIEW_TYPES]
        self.assertIn('list', choices)
        self.assertIn('detail', choices)
        self.assertIn('summary', choices)


class ModelIntegrationTest(TestCase):
    """Integration tests for model relationships."""
    
    def setUp(self):
        """Set up test data."""
        self.source = NewsSource.objects.create(
            name='Test Source',
            domain='test.com',
            base_url='https://test.com'
        )
        self.article = Article.objects.create(
            url='https://test.com/article1',
            title='Test Article',
            description='Test description',
            content='Test content',
            published_at=timezone.now(),
            source=self.source
        )
    
    def test_source_article_relationship(self):
        """Test NewsSource to Article relationship."""
        # Test forward relationship
        self.assertEqual(self.article.source, self.source)
        
        # Test reverse relationship
        self.assertIn(self.article, self.source.articles.all())
    
    def test_article_view_relationship(self):
        """Test Article to ArticleView relationship."""
        view = ArticleView.objects.create(
            article=self.article,
            view_type='detail'
        )
        
        # Test forward relationship
        self.assertEqual(view.article, self.article)
        
        # Test reverse relationship
        self.assertIn(view, self.article.views.all())
    
    def test_cascade_delete(self):
        """Test cascade delete behavior."""
        # Create a view for the article
        ArticleView.objects.create(
            article=self.article,
            view_type='detail'
        )
        
        # Delete the source (should cascade to article and views)
        source_id = self.source.id
        self.source.delete()
        
        # Check that source is deleted
        self.assertFalse(NewsSource.objects.filter(id=source_id).exists())
        
        # Check that article is deleted
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())
        
        # Check that views are deleted
        self.assertEqual(ArticleView.objects.count(), 0) 