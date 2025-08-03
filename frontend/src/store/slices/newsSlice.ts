import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  Article,
  ArticleDetail,
  NewsSource,
  NewsFilters,
  PaginationState,
  SearchRequest,
} from '../../types';
import { apiService } from '../../services/api';

// Async thunks
export const fetchArticles = createAsyncThunk(
  'news/fetchArticles',
  async (params?: { page?: number; page_size?: number; source?: number; ordering?: string; search?: string }) => {
    const response = await apiService.getArticles(params);
    return response;
  }
);

export const fetchArticle = createAsyncThunk(
  'news/fetchArticle',
  async (id: number) => {
    const response = await apiService.getArticle(id);
    return response;
  }
);

export const fetchSources = createAsyncThunk(
  'news/fetchSources',
  async () => {
    const response = await apiService.getSources();
    return response;
  }
);

export const searchArticles = createAsyncThunk(
  'news/searchArticles',
  async (searchRequest: SearchRequest) => {
    const response = await apiService.searchArticles(searchRequest);
    return response;
  }
);

export const fetchArticleSummary = createAsyncThunk(
  'news/fetchArticleSummary',
  async (id: number) => {
    const response = await apiService.getArticleSummary(id);
    return response;
  }
);

// Initial state
interface NewsState {
  articles: Article[];
  sources: NewsSource[];
  currentArticle: ArticleDetail | null;
  loading: boolean;
  error: string | null;
  filters: NewsFilters;
  pagination: PaginationState;
  searchResults: Article[];
  searchLoading: boolean;
  searchError: string | null;
}

const initialState: NewsState = {
  articles: [],
  sources: [],
  currentArticle: null,
  loading: false,
  error: null,
  filters: {},
  pagination: {
    currentPage: 1,
    pageSize: 20,
    totalCount: 0,
  },
  searchResults: [],
  searchLoading: false,
  searchError: null,
};

// Slice
const newsSlice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<NewsFilters>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setCurrentArticle: (state, action: PayloadAction<ArticleDetail | null>) => {
      state.currentArticle = action.payload;
    },
    clearError: (state) => {
      state.error = null;
      state.searchError = null;
    },
    setPagination: (state, action: PayloadAction<Partial<PaginationState>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
      state.searchError = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Articles
    builder
      .addCase(fetchArticles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchArticles.fulfilled, (state, action) => {
        state.loading = false;
        state.articles = action.payload.results;
        state.pagination.totalCount = action.payload.count;
        state.pagination.currentPage = 1;
      })
      .addCase(fetchArticles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch articles';
      });

    // Fetch Article
    builder
      .addCase(fetchArticle.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchArticle.fulfilled, (state, action) => {
        state.loading = false;
        state.currentArticle = action.payload;
      })
      .addCase(fetchArticle.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch article';
      });

    // Fetch Sources
    builder
      .addCase(fetchSources.pending, (state) => {
        // Don't set loading for sources as it's usually loaded once
      })
      .addCase(fetchSources.fulfilled, (state, action) => {
        state.sources = action.payload;
      })
      .addCase(fetchSources.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch sources';
      });

    // Search Articles
    builder
      .addCase(searchArticles.pending, (state) => {
        state.searchLoading = true;
        state.searchError = null;
      })
      .addCase(searchArticles.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload.results;
        state.pagination.totalCount = action.payload.count;
      })
      .addCase(searchArticles.rejected, (state, action) => {
        state.searchLoading = false;
        state.searchError = action.error.message || 'Failed to search articles';
      });

    // Fetch Article Summary
    builder
      .addCase(fetchArticleSummary.fulfilled, (state, action) => {
        if (state.currentArticle) {
          state.currentArticle.summary = action.payload.summary;
          state.currentArticle.summary_generated_at = action.payload.generated_at;
        }
      });
  },
});

export const {
  setFilters,
  clearFilters,
  setCurrentArticle,
  clearError,
  setPagination,
  clearSearchResults,
} = newsSlice.actions;

export default newsSlice.reducer; 