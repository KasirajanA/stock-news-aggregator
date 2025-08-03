"""
Views for the news app.
"""
import time
from django.db.models import Q, Count, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import NewsSource, Article, SearchLog, ArticleView
from .serializers import (
    NewsSourceSerializer, NewsSourceListSerializer,
    ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer,
    ArticleSummarySerializer, SearchLogSerializer, ArticleViewSerializer,
    SearchRequestSerializer
)


class NewsSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NewsSource model."""
    queryset = NewsSource.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'domain']
    ordering_fields = ['name', 'created_at', 'last_scraped_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return NewsSourceListSerializer
        return NewsSourceSerializer
    
    @action(detail=True, methods=['post'])
    def scrape(self, request, pk=None):
        """Trigger scraping for a specific source."""
        source = self.get_object()
        
        try:
            from .scrapers import scrape_source
            count = scrape_source(source)
            
            return Response({
                'success': True,
                'source': source.name,
                'articles_scraped': count,
                'message': f'Successfully scraped {count} articles from {source.name}'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'source': source.name,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Article model."""
    queryset = Article.objects.filter(is_active=True).select_related('source')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'is_active']
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['published_at', 'created_at', 'word_count', 'reading_time']
    ordering = ['-published_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list to trigger on-demand scraping when news page is loaded."""
        # Trigger scraping on demand (but don't wait for it)
        try:
            from .services import trigger_scraping_on_demand
            # Run scraping in background thread to avoid blocking the response
            import threading
            threading.Thread(target=trigger_scraping_on_demand, daemon=True).start()
        except Exception as e:
            logger.error(f"Error triggering on-demand scraping: {e}")
        
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to log article view."""
        article = self.get_object()
        
        # Log the view
        ArticleView.objects.create(
            article=article,
            view_type='detail',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=self.get_client_ip(request),
            session_id=request.session.session_key
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get or generate article summary."""
        article = self.get_object()
        start_time = time.time()
        
        # Check if summary exists
        if article.summary:
            processing_time = time.time() - start_time
            return Response({
                'summary': article.summary,
                'is_cached': True,
                'processing_time': round(processing_time, 3)
            })
        
        # Generate summary using AI
        try:
            from .summarizer import get_summary_with_stats
            
            # Combine title and content for better summarization
            text_to_summarize = f"{article.title}\n\n{article.content}"
            
            result = get_summary_with_stats(text_to_summarize)
            
            if result['success']:
                summary = result['summary']
                stats = result['stats']
                
                # Save the summary to the article
                article.summary = summary
                article.summary_generated_at = timezone.now()
                article.save()
                
                processing_time = time.time() - start_time
                
                return Response({
                    'summary': summary,
                    'is_cached': False,
                    'processing_time': round(processing_time, 3),
                    'stats': stats
                })
            else:
                return Response({
                    'error': 'Failed to generate summary',
                    'details': result.get('error', 'Unknown error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error generating summary for article {article.id}: {e}")
            return Response({
                'error': 'Failed to generate summary',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchView(APIView):
    """Search functionality for articles."""
    
    def get(self, request):
        """Handle search requests."""
        serializer = SearchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        start_time = time.time()
        
        # Build query
        queryset = Article.objects.filter(is_active=True).select_related('source')
        
        # Apply search
        if data['query']:
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(content__icontains=data['query'])
            )
        
        # Apply filters
        if data.get('source'):
            queryset = queryset.filter(source_id=data['source'])
        
        if data.get('date_from'):
            queryset = queryset.filter(published_at__gte=data['date_from'])
        
        if data.get('date_to'):
            queryset = queryset.filter(published_at__lte=data['date_to'])
        
        # Order by relevance (simple implementation)
        queryset = queryset.order_by('-published_at')
        
        # Pagination
        page_size = data.get('page_size', 20)
        page = data.get('page', 1)
        start = (page - 1) * page_size
        end = start + page_size
        
        articles = queryset[start:end]
        total_count = queryset.count()
        
        # Log search
        execution_time = time.time() - start_time
        SearchLog.objects.create(
            query=data['query'],
            result_count=total_count,
            execution_time=execution_time,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=self.get_client_ip(request)
        )
        
        # Serialize results
        serializer = ArticleListSerializer(articles, many=True)
        
        return Response({
            'query': data['query'],
            'results': serializer.data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'execution_time': round(execution_time, 3),
            'has_next': end < total_count,
            'has_previous': page > 1
        })
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ScrapingView(APIView):
    """API endpoint to trigger news scraping."""
    
    def post(self, request):
        """Trigger scraping for all sources or a specific source."""
        source_name = request.data.get('source')
        force = request.data.get('force', False)
        
        try:
            from .services import ScrapingService
            
            if source_name:
                # Scrape specific source
                result = ScrapingService.scrape_single_source_with_status(source_name)
                if result['success']:
                    return Response(result)
                else:
                    return Response(result, status=status.HTTP_404_NOT_FOUND)
            else:
                # Scrape all sources
                result = ScrapingService.scrape_all_sources_with_status()
                if result['success']:
                    return Response(result)
                else:
                    return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScrapingStatusView(APIView):
    """API endpoint to get scraping status and control."""
    
    def get(self, request):
        """Get current scraping status."""
        try:
            from .services import get_scraping_status, ScrapingService
            
            status = get_scraping_status()
            sources_status = ScrapingService.get_sources_status()
            
            return Response({
                'scheduler_status': status,
                'sources_status': sources_status,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Control the scraping scheduler."""
        action = request.data.get('action')
        
        try:
            from .services import start_automatic_scraping, stop_automatic_scraping
            
            if action == 'start':
                start_automatic_scraping()
                return Response({
                    'success': True,
                    'message': 'Automatic scraping scheduler started'
                })
            elif action == 'stop':
                stop_automatic_scraping()
                return Response({
                    'success': True,
                    'message': 'Automatic scraping scheduler stopped'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid action. Use "start" or "stop"'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Health check endpoint."""
    
    def get(self, request):
        """Return system health status."""
        try:
            # Check database connectivity
            article_count = Article.objects.count()
            source_count = NewsSource.objects.count()
            
            return Response({
                'status': 'healthy',
                'database': 'connected',
                'article_count': article_count,
                'source_count': source_count,
                'timestamp': timezone.now()
            })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 