"""
URL patterns for the news app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'news', views.ArticleViewSet, basename='article')
router.register(r'sources', views.NewsSourceViewSet, basename='source')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.SearchView.as_view(), name='search'),
    path('scrape/', views.ScrapingView.as_view(), name='scrape'),
    path('scraping-status/', views.ScrapingStatusView.as_view(), name='scraping-status'),
] 