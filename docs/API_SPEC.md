# Stock News Aggregator - REST API Specification

## Overview
This document defines the REST API endpoints for the Stock News Aggregator backend built with Django + Django ORM. The API provides endpoints for news management, search functionality, AI summarization, and market data integration.

## Base Information
- **Framework**: Django 4.2+
- **ORM**: Django ORM
- **Authentication**: JWT-based authentication (for future user features)
- **Content-Type**: `application/json`
- **Base URL**: `/api/v1/`

---

## 1. News Articles Module

### 1.1 Get News List
- **Module/Resource**: News Articles
- **Endpoint**: `GET /api/v1/news`
- **Description**: Retrieve a paginated list of news articles with optional filtering and search
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**:
  - `page` (integer, optional): Page number for pagination (default: 1)
  - `page_size` (integer, optional): Number of items per page (default: 20, max: 100)
  - `search` (string, optional): Search query for title, description, and content
  - `source` (string, optional): Filter by news source name
  - `date_from` (string, optional): Filter articles published from this date (YYYY-MM-DD)
  - `date_to` (string, optional): Filter articles published until this date (YYYY-MM-DD)
  - `sort_by` (string, optional): Sort field (published_at, created_at, title) (default: published_at)
  - `sort_order` (string, optional): Sort order (asc, desc) (default: desc)
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "articles": [
        {
          "id": 1,
          "title": "Buy KPR Mill; target of Rs 1287: Sharekhan",
          "description": "Sharekhan is bullish on KPR Mill has recommended buy rating...",
          "url": "https://www.moneycontrol.com/news/business/stocks/...",
          "published_at": "2025-01-15T10:30:00Z",
          "source": {
            "id": 1,
            "name": "MoneyControl",
            "domain": "moneycontrol.com"
          },
          "word_count": 245,
          "reading_time": 2
        }
      ],
      "pagination": {
        "current_page": 1,
        "total_pages": 50,
        "total_items": 1000,
        "page_size": 20,
        "has_next": true,
        "has_previous": false
      }
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid query parameters
  - `500 Internal Server Error`: Server error
- **Security Notes**: Input validation for query parameters, rate limiting (100 requests/minute)

### 1.2 Get News Article Detail
- **Module/Resource**: News Articles
- **Endpoint**: `GET /api/v1/news/{id}`
- **Description**: Retrieve detailed information about a specific news article
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**: None
- **Path Parameters**:
  - `id` (integer, required): Article ID
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "title": "Buy KPR Mill; target of Rs 1287: Sharekhan",
      "description": "Sharekhan is bullish on KPR Mill has recommended buy rating...",
      "content": "Full article content here...",
      "url": "https://www.moneycontrol.com/news/business/stocks/...",
      "published_at": "2025-01-15T10:30:00Z",
      "source": {
        "id": 1,
        "name": "MoneyControl",
        "domain": "moneycontrol.com"
      },
             "summary": "AI-generated summary of the article...",
       "summary_generated_at": "2025-01-15T10:40:00Z",
      "word_count": 245,
      "reading_time": 2,
      "created_at": "2025-01-15T10:35:00Z",
      "last_scraped_at": "2025-01-15T10:35:00Z"
    }
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Article not found
  - `500 Internal Server Error`: Server error
- **Security Notes**: Input validation for article ID

---

## 2. News Summarization Module

### 2.1 Get Article Summary
- **Module/Resource**: News Summarization
- **Endpoint**: `GET /api/v1/news/{id}/summary`
- **Description**: Retrieve existing summary or generate new one if not available
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**: None
- **Path Parameters**:
  - `id` (integer, required): Article ID
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "article_id": 1,
      "summary": "AI-generated summary highlighting key points of the article...",
      "generated_at": "2025-01-15T10:40:00Z",
      "word_count": 85,
      "is_cached": true,
      "processing_time": 0.05
    }
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Article not found
  - `422 Unprocessable Entity`: Article content too short for summarization
  - `500 Internal Server Error`: AI service error or server error
- **Security Notes**: Rate limiting (10 requests/minute per IP), input validation
- **Logic**: Check if summary exists in database, if not generate and store it

---

## 3. Search Module

### 3.1 Search Articles
- **Module/Resource**: Search
- **Endpoint**: `GET /api/v1/search`
- **Description**: Search articles using full-text search across titles, descriptions, and content
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**:
  - `q` (string, required): Search query
  - `page` (integer, optional): Page number for pagination (default: 1)
  - `page_size` (integer, optional): Number of items per page (default: 20, max: 100)
  - `source` (string, optional): Filter by news source
  - `date_from` (string, optional): Filter by date range (YYYY-MM-DD)
  - `date_to` (string, optional): Filter by date range (YYYY-MM-DD)
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "query": "KPR Mill",
      "articles": [
        {
          "id": 1,
          "title": "Buy KPR Mill; target of Rs 1287: Sharekhan",
          "description": "Sharekhan is bullish on KPR Mill has recommended buy rating...",
          "url": "https://www.moneycontrol.com/news/business/stocks/...",
          "published_at": "2025-01-15T10:30:00Z",
          "source": {
            "id": 1,
            "name": "MoneyControl",
            "domain": "moneycontrol.com"
          },
          "relevance_score": 0.95
        }
      ],
      "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_items": 100,
        "page_size": 20,
        "has_next": true,
        "has_previous": false
      },
      "search_metadata": {
        "execution_time": 0.15,
        "total_results": 100
      }
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing or invalid search query
  - `500 Internal Server Error`: Server error
- **Security Notes**: Input validation, rate limiting (50 requests/minute), SQL injection prevention

---

## 4. Market Data Module

### 4.1 Get Market Indices
- **Module/Resource**: Market Data
- **Endpoint**: `GET /api/v1/market-indices`
- **Description**: Fetch current market indices data from third-party API
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**: None
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "last_updated": "2025-01-15T10:45:00Z",
      "indices": {
        "NIFTY": {
          "current_value": 25003.05,
          "change_amount": 123.45,
          "change_percentage": 0.49,
          "previous_close": 24879.60,
          "day_high": 25100.25,
          "day_low": 24850.10
        },
        "SENSEX": {
          "current_value": 82188.99,
          "change_amount": 456.78,
          "change_percentage": 0.56,
          "previous_close": 81732.21,
          "day_high": 82300.50,
          "day_low": 81650.75
        }
      },
      "source": "third_party_api",
      "fetch_time": 0.85
    }
  }
  ```
- **Error Responses**:
  - `503 Service Unavailable`: Third-party API unavailable
  - `500 Internal Server Error`: Server error
- **Security Notes**: Rate limiting (30 requests/minute), API key management for third-party service

---

## 5. News Sources Module

### 5.1 Get News Sources
- **Module/Resource**: News Sources
- **Endpoint**: `GET /api/v1/sources`
- **Description**: Retrieve list of all news sources
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**:
  - `active` (boolean, optional): Filter by active status (default: true)
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "sources": [
        {
          "id": 1,
          "name": "MoneyControl",
          "domain": "moneycontrol.com",
          "base_url": "https://www.moneycontrol.com",
          "is_active": true,
          "last_scraped_at": "2025-01-15T10:30:00Z",
          "article_count": 1500
        }
      ]
    }
  }
  ```
- **Error Responses**:
  - `500 Internal Server Error`: Server error
- **Security Notes**: Input validation

---

## 6. Analytics Module

### 6.1 Get Popular Articles
- **Module/Resource**: Analytics
- **Endpoint**: `GET /api/v1/analytics/popular-articles`
- **Description**: Retrieve most viewed articles based on view statistics
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**:
  - `limit` (integer, optional): Number of articles to return (default: 10, max: 50)
  - `period` (string, optional): Time period (today, week, month) (default: week)
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "period": "week",
      "articles": [
        {
          "id": 1,
          "title": "Buy KPR Mill; target of Rs 1287: Sharekhan",
          "view_count": 1250,
          "source": {
            "id": 1,
            "name": "MoneyControl"
          },
          "published_at": "2025-01-15T10:30:00Z"
        }
      ]
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid parameters
  - `500 Internal Server Error`: Server error
- **Security Notes**: Input validation, rate limiting (20 requests/minute)

---

## 7. Health Check Module

### 7.1 Health Check
- **Module/Resource**: System Health
- **Endpoint**: `GET /api/v1/health`
- **Description**: Check system health and status
- **Authentication**: None (public endpoint)
- **Request Headers**: 
  - `Content-Type: application/json`
  - `Accept: application/json`
- **Query Parameters**: None
- **Path Parameters**: None
- **Success Response**:
  ```json
  {
    "status": "success",
    "data": {
      "service": "Stock News Aggregator API",
      "version": "1.0.0",
      "timestamp": "2025-01-15T10:50:00Z",
      "database": "connected",
      "third_party_apis": {
        "market_data": "available",
        "ai_summarization": "available"
      },
      "uptime": "2 days, 5 hours, 30 minutes"
    }
  }
  ```
- **Error Responses**:
  - `503 Service Unavailable`: Service unavailable
- **Security Notes**: No sensitive information in response

---

## 8. Error Response Format

### Standard Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "page",
      "issue": "Must be a positive integer"
    }
  },
  "timestamp": "2025-01-15T10:50:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request parameters
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVICE_UNAVAILABLE`: Third-party service unavailable
- `INTERNAL_SERVER_ERROR`: Server error

---

## 9. Authentication (Future Implementation)

### 9.1 User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Description**: Register new user account
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "user123",
    "password": "securepassword123"
  }
  ```

### 9.2 User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Authenticate user and return JWT token
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```

### 9.3 User Profile
- **Endpoint**: `GET /api/v1/auth/profile`
- **Description**: Get current user profile
- **Authentication**: JWT Required
- **Headers**: `Authorization: Bearer <jwt_token>`

---

## 10. Security Considerations

### 10.1 Rate Limiting
- **Public Endpoints**: 100 requests/minute per IP
- **Search Endpoints**: 50 requests/minute per IP
- **Summary Endpoints**: 10 requests/minute per IP
- **Market Data Endpoints**: 30 requests/minute per IP

### 10.2 Input Validation
- **Query Parameters**: Validate all query parameters for type and range
- **Path Parameters**: Validate integer IDs and string identifiers
- **Request Body**: Validate JSON structure and required fields

### 10.3 CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com"
]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
```

### 10.4 API Versioning
- **Current Version**: v1
- **Version Header**: `Accept: application/vnd.api+json;version=1`
- **URL Versioning**: `/api/v1/`

---

## 11. Implementation Notes

### 11.1 Django Settings
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
    }
}
```

### 11.2 URL Configuration
```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'sources', SourceViewSet, basename='sources')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/search/', SearchView.as_view(), name='search'),
    path('api/v1/market-indices/', MarketIndicesView.as_view(), name='market-indices'),
    path('api/v1/health/', HealthCheckView.as_view(), name='health'),
]
```

### 11.3 Summary Generation Logic
```python
# Summary generation service logic
class SummaryService:
    def get_summary(self, article_id: int) -> Dict:
        article = Article.objects.get(id=article_id)
        
        # Check if summary already exists
        if article.summary:
            return {
                'summary': article.summary,
                'is_cached': True,
                'processing_time': 0.05
            }
        
        # Generate new summary if not exists
        summary = self.generate_ai_summary(article.content)
        article.summary = summary
        article.save()
        
        return {
            'summary': summary,
            'is_cached': False,
            'processing_time': 2.5
        }
    
    def generate_ai_summary(self, content: str) -> str:
        # AI summarization logic here
        # Call third-party AI service
        pass
```

This API specification provides a comprehensive foundation for the Stock News Aggregator backend, covering all required functionality while maintaining security, performance, and scalability considerations. 