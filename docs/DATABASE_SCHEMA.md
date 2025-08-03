# Stock News Aggregator - Database Schema

## Overview
This document defines the complete database schema for the Stock News Aggregator application. The schema is designed to support news aggregation, search functionality, AI summarization, market data tracking, and future enhancements while maintaining normalization and performance.

## Database Design Principles
- **Normalization**: 3NF compliance where appropriate
- **Performance**: Optimized for frequent queries (search, pagination, market data)
- **Scalability**: Designed to handle 10,000+ articles efficiently
- **Extensibility**: Support for future features and enhancements

---

## 1. Core Tables

### 1.1 Articles Table
**Purpose**: Store all scraped news articles with metadata and content

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique article identifier |
| `url` | VARCHAR(2048) | NOT NULL, UNIQUE | Original article URL (max length for URLs) |
| `title` | VARCHAR(500) | NOT NULL | Article headline |
| `description` | TEXT | NOT NULL | Article summary/description |
| `summary` | TEXT | NULL | AI-generated summary (stored after first generation) |
| `content` | LONGTEXT | NOT NULL | Full article content |
| `published_at` | TIMESTAMP | NOT NULL | Original publication date |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |
| `last_scraped_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last scraping timestamp |
| `source_id` | INT | NOT NULL, FOREIGN KEY | Reference to news source |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete flag |
| `word_count` | INT | NULL | Article word count for analytics |
| `reading_time` | INT | NULL | Estimated reading time in minutes |

**Indexes:**
- `idx_articles_url` (UNIQUE) on `url`
- `idx_articles_published_at` on `published_at` (for chronological ordering)
- `idx_articles_source_id` on `source_id` (for source filtering)
- `idx_articles_created_at` on `created_at` (for recent articles)
- `idx_articles_title_content` (FULLTEXT) on `title`, `description`, `content` (for search)

### 1.2 News Sources Table
**Purpose**: Track news sources and their metadata

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique source identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Source name (e.g., "LiveMint") |
| `domain` | VARCHAR(255) | NOT NULL, UNIQUE | Source domain |
| `base_url` | VARCHAR(500) | NOT NULL | Base URL for scraping |
| `scraping_frequency` | INT | NOT NULL, DEFAULT 3600 | Scraping interval in seconds |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether source is active |
| `last_scraped_at` | TIMESTAMP | NULL | Last successful scraping |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_sources_name` (UNIQUE) on `name`
- `idx_sources_domain` (UNIQUE) on `domain`
- `idx_sources_active` on `is_active` (for active source filtering)



---

## 2. Search and Analytics Tables

### 2.1 Search Logs Table
**Purpose**: Track search queries for analytics and improvement

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique log identifier |
| `query` | VARCHAR(500) | NOT NULL | Search query text |
| `result_count` | INT | NOT NULL | Number of results returned |
| `execution_time` | DECIMAL(10,3) | NULL | Query execution time in seconds |
| `user_agent` | VARCHAR(500) | NULL | User agent string |
| `ip_address` | VARCHAR(45) | NULL | User IP address (IPv6 compatible) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Log creation timestamp |

**Indexes:**
- `idx_search_logs_query` on `query` (for query analysis)
- `idx_search_logs_created_at` on `created_at` (for time-based analysis)
- `idx_search_logs_execution_time` on `execution_time` (for performance monitoring)

### 2.2 Article Views Table
**Purpose**: Track article view statistics for analytics

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique view identifier |
| `article_id` | BIGINT | NOT NULL, FOREIGN KEY | Reference to article |
| `view_type` | ENUM('list', 'detail', 'summary') | NOT NULL | Type of view |
| `user_agent` | VARCHAR(500) | NULL | User agent string |
| `ip_address` | VARCHAR(45) | NULL | User IP address |
| `session_id` | VARCHAR(100) | NULL | Session identifier |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | View timestamp |

**Indexes:**
- `idx_article_views_article_id` on `article_id` (for article popularity)
- `idx_article_views_created_at` on `created_at` (for time-based analytics)
- `idx_article_views_type` on `view_type` (for view type analysis)

---

## 3. Future Enhancement Tables

### 3.1 Users Table (Future)
**Purpose**: Support user accounts and personalization

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| `username` | VARCHAR(50) | NULL, UNIQUE | Username |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_users_email` (UNIQUE) on `email`
- `idx_users_username` (UNIQUE) on `username`

### 3.2 User Preferences Table (Future)
**Purpose**: Store user preferences and settings

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique preference identifier |
| `user_id` | BIGINT | NOT NULL, FOREIGN KEY | Reference to user |
| `preference_key` | VARCHAR(100) | NOT NULL | Preference key |
| `preference_value` | TEXT | NOT NULL | Preference value (JSON) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_user_preferences_user_key` (UNIQUE) on `user_id`, `preference_key`

### 3.3 Article Categories Table (Future)
**Purpose**: Categorize articles for better organization

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique category identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Category name |
| `description` | TEXT | NULL | Category description |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Category status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_article_categories_name` (UNIQUE) on `name`

### 3.4 Article Category Mapping Table (Future)
**Purpose**: Many-to-many relationship between articles and categories

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique mapping identifier |
| `article_id` | BIGINT | NOT NULL, FOREIGN KEY | Reference to article |
| `category_id` | INT | NOT NULL, FOREIGN KEY | Reference to category |
| `confidence_score` | DECIMAL(3,2) | NULL | AI confidence in categorization |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Mapping creation timestamp |

**Indexes:**
- `idx_article_category_mapping_article` on `article_id`
- `idx_article_category_mapping_category` on `category_id`
- `idx_article_category_mapping_unique` (UNIQUE) on `article_id`, `category_id`

---

## 4. Relationships

### 4.1 Current Relationships
- **Articles** → **News Sources**: Many-to-One (articles.source_id → sources.id)
- **Article Views** → **Articles**: Many-to-One (article_views.article_id → articles.id)

### 4.2 Future Relationships
- **User Preferences** → **Users**: Many-to-One (user_preferences.user_id → users.id)
- **Article Category Mapping** → **Articles**: Many-to-One (article_category_mapping.article_id → articles.id)
- **Article Category Mapping** → **Article Categories**: Many-to-One (article_category_mapping.category_id → article_categories.id)

---

## 5. Django ORM Models

```python
# models.py

from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class NewsSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    base_url = models.CharField(max_length=500)
    scraping_frequency = models.IntegerField(default=3600)  # seconds
    is_active = models.BooleanField(default=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_sources'
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

class Article(models.Model):
    url = models.CharField(max_length=2048, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    summary = models.TextField(null=True, blank=True)
    content = models.TextField()
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped_at = models.DateTimeField(auto_now_add=True)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    word_count = models.IntegerField(null=True, blank=True)
    reading_time = models.IntegerField(null=True, blank=True)
    
    # Search vector for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        db_table = 'articles'
        indexes = [
            models.Index(fields=['published_at']),
            models.Index(fields=['source']),
            models.Index(fields=['created_at']),
            GinIndex(fields=['search_vector']),  # For full-text search
        ]

    def __str__(self):
        return self.title



class SearchLog(models.Model):
    query = models.CharField(max_length=500)
    result_count = models.IntegerField()
    execution_time = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_logs'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['execution_time']),
        ]

class ArticleView(models.Model):
    VIEW_TYPES = [
        ('list', 'List View'),
        ('detail', 'Detail View'),
        ('summary', 'Summary View'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    view_type = models.CharField(max_length=10, choices=VIEW_TYPES)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_views'
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['created_at']),
            models.Index(fields=['view_type']),
        ]
```

---

## 6. SQL DDL Statements (PostgreSQL)

```sql
-- Create tables for Stock News Aggregator

-- 1. News Sources Table
CREATE TABLE news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    domain VARCHAR(255) NOT NULL UNIQUE,
    base_url VARCHAR(500) NOT NULL,
    scraping_frequency INTEGER NOT NULL DEFAULT 3600,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_scraped_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Articles Table
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR(2048) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    summary TEXT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_id INTEGER NOT NULL REFERENCES news_sources(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    word_count INTEGER NULL,
    reading_time INTEGER NULL
);



-- 4. Search Logs Table
CREATE TABLE search_logs (
    id BIGSERIAL PRIMARY KEY,
    query VARCHAR(500) NOT NULL,
    result_count INTEGER NOT NULL,
    execution_time DECIMAL(10,3) NULL,
    user_agent VARCHAR(500) NULL,
    ip_address INET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Article Views Table
CREATE TABLE article_views (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL REFERENCES articles(id),
    view_type VARCHAR(10) NOT NULL CHECK (view_type IN ('list', 'detail', 'summary')),
    user_agent VARCHAR(500) NULL,
    ip_address INET NULL,
    session_id VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_published_at ON articles(published_at);
CREATE INDEX idx_articles_source_id ON articles(source_id);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_articles_title_content ON articles USING gin(to_tsvector('english', title || ' ' || description || ' ' || content));

CREATE INDEX idx_sources_name ON news_sources(name);
CREATE INDEX idx_sources_domain ON news_sources(domain);
CREATE INDEX idx_sources_active ON news_sources(is_active);



CREATE INDEX idx_search_logs_query ON search_logs(query);
CREATE INDEX idx_search_logs_created_at ON search_logs(created_at);
CREATE INDEX idx_search_logs_execution_time ON search_logs(execution_time);

CREATE INDEX idx_article_views_article_id ON article_views(article_id);
CREATE INDEX idx_article_views_created_at ON article_views(created_at);
CREATE INDEX idx_article_views_type ON article_views(view_type);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_news_sources_updated_at BEFORE UPDATE ON news_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 7. Performance Considerations

### 7.1 Indexing Strategy
- **Primary Keys**: Auto-incrementing BIGINT for scalability
- **Full-text Search**: GIN index on article content for fast search
- **Time-based Queries**: Indexes on timestamp fields for chronological ordering
- **Foreign Keys**: Indexed for join performance

### 7.2 Partitioning Strategy (Future)
- **Articles Table**: Partition by `published_at` date for large datasets
- **Search Logs Table**: Partition by `created_at` for time-series data

### 7.3 Caching Strategy
- **Redis**: Cache frequently accessed articles and market data
- **CDN**: Static assets and cached content delivery
- **Application Cache**: In-memory caching for search results

### 7.4 Data Retention
- **Articles**: Retain for 1 year (configurable)
- **Article Summaries**: Retain with articles (deleted when article is deleted)
- **Search Logs**: Retain for 6 months for analytics
- **Article Views**: Retain for 1 year for popularity tracking

---

## 8. Security Considerations

### 8.1 Data Protection
- **Input Validation**: All user inputs sanitized
- **SQL Injection Prevention**: Parameterized queries only
- **Access Control**: Database user with minimal required privileges
- **Encryption**: Sensitive data encrypted at rest

### 8.2 Privacy Compliance
- **IP Addresses**: Stored for analytics but not linked to personal data
- **User Agents**: Stored for debugging but anonymized
- **Session Data**: Temporary storage with automatic cleanup

---

## 9. Migration Strategy

### 9.1 Development to Production
1. **SQLite to PostgreSQL**: Use Django's built-in migration system
2. **Data Migration**: Script to transfer existing data
3. **Index Optimization**: Create indexes after data migration
4. **Performance Tuning**: Adjust PostgreSQL settings for production

### 9.2 Schema Evolution
- **Backward Compatibility**: Maintain API compatibility during migrations
- **Rollback Strategy**: Database backups before major schema changes
- **Feature Flags**: Gradual rollout of new features



This schema provides a solid foundation for the Stock News Aggregator application, supporting current requirements while allowing for future enhancements and scalability. 