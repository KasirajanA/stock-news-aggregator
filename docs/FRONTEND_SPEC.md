# Stock News Aggregator - Frontend Architecture Specification

## Overview
This document defines the frontend architecture for the Stock News Aggregator application, designed to provide a modern, responsive, and user-friendly interface for accessing stock market news and real-time market data.

## 1. Overall Purpose and Tech Stack

### **Primary Purpose**
Create a unified, responsive web application that aggregates stock market news from multiple sources, provides AI-powered summaries, and displays real-time market indices with an intuitive user interface.

### **Proposed Tech Stack**
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit (RTK) for global state, React Query for server state
- **Styling Library**: Material-UI (MUI) v5 with custom theme
- **Data Fetching**: React Query (TanStack Query) for API integration
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Testing**: Jest + React Testing Library
- **Code Quality**: ESLint + Prettier
- **Package Manager**: npm/yarn

---

## 2. Screens/Pages

### **2.1 Home Page (Dashboard)**
- **Route**: `/`
- **Purpose**: Main landing page with news feed, market overview, and search functionality
- **Key Features**:
  - News article list with pagination
  - Market indices display with refresh button
  - Search bar for quick article search
  - Filter options (source, date range)
  - Responsive grid layout

### **2.2 Article Detail Page**
- **Route**: `/article/:id`
- **Purpose**: Detailed view of individual news article
- **Key Features**:
  - Full article content display
  - AI summary generation/display
  - Source attribution and metadata
  - Back to list navigation
  - Share functionality

### **2.3 Search Results Page**
- **Route**: `/search?q=:query`
- **Purpose**: Display search results with filtering options
- **Key Features**:
  - Search results with relevance scoring
  - Advanced filtering (source, date range)
  - Search query highlighting
  - Pagination for results

### **2.4 Popular Articles Page**
- **Route**: `/popular`
- **Purpose**: Show most viewed articles based on analytics
- **Key Features**:
  - Trending articles list
  - View count display
  - Time period filtering (today, week, month)

---

## 3. Key Reusable Components

### **3.1 Layout Components**

#### **AppLayout**
```typescript
interface AppLayoutProps {
  children: React.ReactNode;
  title?: string;
  showBackButton?: boolean;
}
```
- **Purpose**: Main application layout with header, navigation, and content area
- **Features**: Responsive header, navigation menu, footer

#### **Header**
```typescript
interface HeaderProps {
  onSearch?: (query: string) => void;
  onRefreshMarketData?: () => void;
  marketData?: MarketData;
}
```
- **Purpose**: Application header with search, market data, and navigation
- **Features**: Search bar, market indices display, refresh button

### **3.2 News Components**

#### **ArticleCard**
```typescript
interface ArticleCardProps {
  article: Article;
  onSummaryClick?: (articleId: number) => void;
  onArticleClick?: (articleId: number) => void;
  variant?: 'compact' | 'detailed';
}
```
- **Purpose**: Display individual news article in list format
- **Features**: Title, description, source, published date, summary button

#### **ArticleList**
```typescript
interface ArticleListProps {
  articles: Article[];
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  onArticleClick?: (articleId: number) => void;
}
```
- **Purpose**: Paginated list of news articles
- **Features**: Infinite scroll, loading states, empty states

#### **ArticleDetail**
```typescript
interface ArticleDetailProps {
  article: Article;
  summary?: ArticleSummary;
  onGenerateSummary?: () => void;
  summaryLoading?: boolean;
}
```
- **Purpose**: Detailed article view with full content and summary
- **Features**: Full content display, summary section, metadata

### **3.3 Market Data Components**

#### **MarketOverview**
```typescript
interface MarketOverviewProps {
  marketData?: MarketData;
  loading?: boolean;
  onRefresh?: () => void;
  lastUpdated?: string;
}
```
- **Purpose**: Display current market indices with refresh functionality
- **Features**: NIFTY/SENSEX values, change indicators, refresh button

#### **MarketIndexCard**
```typescript
interface MarketIndexCardProps {
  index: MarketIndex;
  variant?: 'compact' | 'detailed';
}
```
- **Purpose**: Individual market index display
- **Features**: Current value, change amount, percentage, color coding

### **3.4 Search Components**

#### **SearchBar**
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  defaultValue?: string;
  loading?: boolean;
}
```
- **Purpose**: Search input with autocomplete and suggestions
- **Features**: Debounced search, search history, loading indicator

#### **SearchFilters**
```typescript
interface SearchFiltersProps {
  sources: NewsSource[];
  onFilterChange: (filters: SearchFilters) => void;
  currentFilters: SearchFilters;
}
```
- **Purpose**: Advanced search filtering options
- **Features**: Source selection, date range picker, sort options

### **3.5 Common Components**

#### **LoadingSpinner**
```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary';
  text?: string;
}
```

#### **ErrorBoundary**
```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error }>;
}
```

#### **Pagination**
```typescript
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}
```

---

## 4. State Management Strategy

### **4.1 Global State (Redux Toolkit)**
```typescript
// Store structure
interface RootState {
  ui: UIState;
  search: SearchState;
  market: MarketState;
  user: UserState;
}

interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  notifications: Notification[];
}

interface SearchState {
  recentSearches: string[];
  searchHistory: SearchQuery[];
}

interface MarketState {
  lastRefresh: string;
  autoRefresh: boolean;
}
```

### **4.2 Server State (React Query)**
```typescript
// Query keys
const queryKeys = {
  articles: ['articles'],
  article: (id: number) => ['article', id],
  search: (query: string) => ['search', query],
  marketData: ['market-data'],
  popularArticles: ['popular-articles'],
  sources: ['sources'],
} as const;
```

### **4.3 Local State (useState/useReducer)**
- Form inputs and validation
- UI interactions (modals, dropdowns)
- Component-specific state

---

## 5. API Integration

### **5.1 Home Page**
```typescript
// API endpoints used
- GET /api/v1/news - Article list with pagination
- GET /api/v1/market-indices - Market data
- GET /api/v1/sources - News sources for filtering
```

### **5.2 Article Detail Page**
```typescript
// API endpoints used
- GET /api/v1/news/{id} - Article details
- GET /api/v1/news/{id}/summary - Article summary
```

### **5.3 Search Results Page**
```typescript
// API endpoints used
- GET /api/v1/search - Search results
- GET /api/v1/sources - Sources for filtering
```

### **5.4 Popular Articles Page**
```typescript
// API endpoints used
- GET /api/v1/analytics/popular-articles - Popular articles
```

### **5.5 React Query Hooks**
```typescript
// Custom hooks for API integration
export const useArticles = (params: ArticleParams) => {
  return useQuery({
    queryKey: ['articles', params],
    queryFn: () => api.getArticles(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useArticleSummary = (articleId: number) => {
  return useQuery({
    queryKey: ['article-summary', articleId],
    queryFn: () => api.getArticleSummary(articleId),
    enabled: !!articleId,
  });
};

export const useMarketData = () => {
  return useQuery({
    queryKey: ['market-data'],
    queryFn: () => api.getMarketIndices(),
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};
```

---

## 6. Data Input/Output

### **6.1 Forms and User Input**

#### **Search Form**
```typescript
interface SearchFormData {
  query: string;
  source?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: 'published_at' | 'created_at' | 'title';
  sortOrder?: 'asc' | 'desc';
}
```

#### **Filter Form**
```typescript
interface FilterFormData {
  sources: string[];
  dateRange: [Date | null, Date | null];
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}
```

### **6.2 Data Display**

#### **Article Data Structure**
```typescript
interface Article {
  id: number;
  title: string;
  description: string;
  content: string;
  url: string;
  published_at: string;
  source: NewsSource;
  summary?: string;
  word_count: number;
  reading_time: number;
}
```

#### **Market Data Structure**
```typescript
interface MarketData {
  last_updated: string;
  indices: {
    NIFTY: MarketIndex;
    SENSEX: MarketIndex;
  };
  source: string;
  fetch_time: number;
}
```

---

## 7. UI/UX Considerations

### **7.1 Responsive Design**
- **Mobile First**: Design for mobile devices first, then scale up
- **Breakpoints**: xs (0px), sm (600px), md (900px), lg (1200px), xl (1536px)
- **Grid System**: 12-column responsive grid using MUI Grid
- **Typography**: Responsive font sizes using MUI theme

### **7.2 Loading States**
```typescript
// Loading state components
- Skeleton loaders for article cards
- Shimmer effects for market data
- Progress indicators for summary generation
- Infinite scroll loading indicators
```

### **7.3 Error Handling**
```typescript
// Error handling strategy
- Global error boundary for unhandled errors
- API error handling with user-friendly messages
- Retry mechanisms for failed requests
- Offline state handling
```

### **7.4 Accessibility (WCAG AA)**
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and roles
- **Color Contrast**: Minimum 4.5:1 contrast ratio
- **Focus Management**: Visible focus indicators
- **Alt Text**: Descriptive alt text for images

### **7.5 Optimistic Updates**
- **Search Results**: Immediate display with loading states
- **Market Data**: Show cached data while refreshing
- **Summary Generation**: Show loading state while generating

---

## 8. Routing Strategy

### **8.1 Route Configuration**
```typescript
// App routing structure
const routes = [
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/article/:id',
    element: <ArticleDetailPage />,
  },
  {
    path: '/search',
    element: <SearchResultsPage />,
  },
  {
    path: '/popular',
    element: <PopularArticlesPage />,
  },
];
```

### **8.2 Navigation Patterns**
- **Breadcrumbs**: Show current location in app hierarchy
- **Back Navigation**: Browser back button support
- **Deep Linking**: Direct access to articles and search results
- **URL State**: Search queries and filters in URL

### **8.3 Route Guards**
- **404 Handling**: Custom 404 page for invalid routes
- **Loading States**: Route-level loading indicators
- **Error Boundaries**: Route-level error handling

---

## 9. Performance Optimizations

### **9.1 Code Splitting**
```typescript
// Lazy loading for routes
const ArticleDetailPage = lazy(() => import('./pages/ArticleDetailPage'));
const SearchResultsPage = lazy(() => import('./pages/SearchResultsPage'));
```

### **9.2 Image Optimization**
- **Lazy Loading**: Images load as they enter viewport
- **Responsive Images**: Different sizes for different screen sizes
- **WebP Format**: Modern image format with fallbacks

### **9.3 Caching Strategy**
- **React Query**: Automatic caching and background updates
- **Service Worker**: Offline support and caching
- **Local Storage**: User preferences and search history

---

## 10. Theme and Styling

### **10.1 Material-UI Theme**
```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h1: { fontSize: '2.5rem', fontWeight: 600 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.75rem', fontWeight: 500 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});
```

### **10.2 Custom Components**
- **NewsCard**: Custom article card component
- **MarketCard**: Custom market data display
- **SearchBar**: Custom search input with suggestions

---

## 11. Testing Strategy

### **11.1 Unit Testing**
- **Component Testing**: Test individual components in isolation
- **Hook Testing**: Test custom hooks with React Testing Library
- **Utility Testing**: Test utility functions and helpers

### **11.2 Integration Testing**
- **API Integration**: Test API calls and error handling
- **User Flows**: Test complete user journeys
- **State Management**: Test Redux actions and reducers

### **11.3 E2E Testing**
- **Critical Paths**: Test main user flows
- **Cross-browser**: Test in multiple browsers
- **Performance**: Test loading times and responsiveness

---

## 12. Development Workflow

### **12.1 Project Structure**
```
src/
├── components/
│   ├── common/
│   ├── layout/
│   ├── news/
│   ├── market/
│   └── search/
├── pages/
├── hooks/
├── services/
├── store/
├── types/
├── utils/
└── styles/
```

### **12.2 Development Tools**
- **Storybook**: Component development and documentation
- **React DevTools**: State inspection and debugging
- **Redux DevTools**: State management debugging
- **React Query DevTools**: Server state debugging

This frontend architecture specification provides a comprehensive foundation for building a modern, scalable, and user-friendly Stock News Aggregator application that aligns with the PRD requirements and API specification. 