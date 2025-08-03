"""
URL patterns for the market_data app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('market-indices/', views.MarketIndicesView.as_view(), name='market-indices'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
] 