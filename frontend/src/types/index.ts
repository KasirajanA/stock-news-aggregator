// API Response Types
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// News Source Types
export interface NewsSource {
  id: number;
  name: string;
  domain: string;
  base_url: string;
  scraping_frequency: number;
  is_active: boolean;
  last_scraped_at: string | null;
  created_at: string;
  updated_at: string;
  articles_count?: number;
}

// Article Types
export interface Article {
  id: number;
  url: string;
  title: string;
  description: string;
  summary: string | null;
  content: string;
  published_at: string;
  created_at: string;
  updated_at: string;
  last_scraped_at: string;
  source: number | NewsSource; // Can be either ID or full object
  is_active: boolean;
  word_count: number | null;
  reading_time: number | null;
  summary_generated_at?: string;
}

export interface ArticleDetail extends Article {
  source_details: NewsSource;
  view_count?: number;
  popularity_score?: number;
}

// Search Types
export interface SearchRequest {
  query: string;
  source?: number;
  ordering?: string;
  page?: number;
}

export interface SearchResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Article[];
  execution_time?: number;
}

// Summary Types
export interface ArticleSummary {
  summary: string;
  is_cached: boolean;
  processing_time: number;
  generated_at: string;
}

// Market Data Types
export interface MarketIndex {
  name: string;
  value: number;
  change: number;
  change_percentage: number;
  last_updated: string;
}

export interface MarketData {
  indices: MarketIndex[];
  last_updated: string;
  source?: string;
  market_status?: string;
}

// Scraping Types
export interface ScrapingStatus {
  scheduler_status: {
    scheduler_running: boolean;
    last_scrape: string | null;
    next_scheduled_scrape: string | null;
    scraping_interval_seconds: number;
  };
  sources_status: SourceStatus[];
  timestamp: string;
}

export interface SourceStatus {
  id: number;
  name: string;
  domain: string;
  is_active: boolean;
  articles_count: number;
  last_scraped_at: string | null;
  time_since_last: number | null;
  should_scrape: boolean;
  scraping_frequency: number;
}

export interface ScrapingResult {
  success: boolean;
  results?: Record<string, number>;
  total_articles?: number;
  processing_time?: number;
  timestamp?: string;
  sources_scraped?: number;
  error?: string;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalCount: number;
}

// Filter Types
export interface NewsFilters {
  source?: number;
  date_from?: string;
  date_to?: string;
  search_query?: string;
  ordering?: string;
}

// Component Props Types
export interface NewsCardProps {
  article: Article;
  onView: (article: Article) => void;
  onSummary: (article: Article) => void;
}

export interface NewsListProps {
  articles: Article[];
  loading: boolean;
  error: string | null;
  onLoadMore: () => void;
  hasMore: boolean;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export interface MarketIndicesProps {
  data: MarketData;
  loading: boolean;
  onRefresh: () => void;
}

// Redux State Types
export interface RootState {
  news: NewsState;
  market: MarketState;
  ui: UIState;
}

export interface NewsState {
  articles: Article[];
  sources: NewsSource[];
  currentArticle: ArticleDetail | null;
  loading: boolean;
  error: string | null;
  filters: NewsFilters;
  pagination: PaginationState;
}

export interface MarketState {
  data: MarketData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  timestamp: string;
} 