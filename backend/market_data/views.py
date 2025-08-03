"""
Views for the market_data app.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import market_data_service

logger = logging.getLogger(__name__)


class MarketIndicesView(APIView):
    """Market indices data endpoint."""
    
    def get(self, request):
        """Get live market indices data from NSE India with caching."""
        try:
            # Check if force refresh is requested
            force_refresh = request.query_params.get('refresh', '').lower() == 'true'
            
            # Get market data from NSE service
            market_data = market_data_service.get_market_data(force_refresh=force_refresh)
            
            # Return data in the format expected by the frontend
            return Response({
                'indices': market_data['indices'],
                'last_updated': market_data['last_updated'],
                'source': market_data.get('source', 'unknown'),
                'market_status': market_data.get('market_status', 'unknown')
            })
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return Response({
                'status': 'error',
                'message': 'Failed to fetch market data',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Health check endpoint."""
    
    def get(self, request):
        """Return system health status."""
        try:
            # Test market data service
            market_data = market_data_service.get_market_data()
            market_status = market_data_service.get_market_status()
            
            return Response({
                'status': 'healthy',
                'market_data_service': 'operational',
                'market_status': market_status,
                'cache_status': 'enabled',
                'timestamp': market_data['last_updated']
            })
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'market_data_service': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 