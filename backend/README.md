# Stock News Aggregator - Backend

Django backend for the Stock News Aggregator application.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Test Setup
```bash
python test_setup.py
```

## Project Structure

```
backend/
├── stock_news_aggregator/     # Main Django project
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── news/                     # News app
│   ├── models.py            # Article and NewsSource models
│   ├── views.py             # API views
│   └── urls.py              # News app URLs
├── market_data/             # Market data app
│   ├── views.py             # Market data views
│   └── urls.py              # Market data URLs
├── manage.py                # Django management script
├── requirements.txt          # Python dependencies
└── test_setup.py           # Setup verification script
```

## API Endpoints

- `GET /api/v1/news/` - List articles
- `GET /api/v1/news/{id}/` - Article details
- `GET /api/v1/news/{id}/summary/` - Article summary
- `GET /api/v1/search/` - Search articles
- `GET /api/v1/sources/` - List news sources
- `GET /api/v1/market-indices/` - Market data
- `GET /api/v1/health/` - Health check
- `GET /api/v1/analytics/popular-articles/` - Popular articles

## Admin Interface

Access the Django admin at: http://localhost:8000/admin/

## Development

- **Database**: SQLite (development)
- **API Framework**: Django REST Framework
- **CORS**: django-cors-headers
- **Filtering**: django-filter
- **Testing**: pytest-django 