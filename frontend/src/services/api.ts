import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ApiResponse,
  Article,
  ArticleDetail,
  NewsSource,
  SearchRequest,
  SearchResponse,
  ArticleSummary,
  MarketData,
  ScrapingStatus,
  ScrapingResult,
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

console.log('API Base URL:', API_BASE_URL);

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // News Articles API
  async getArticles(params?: {
    page?: number;
    page_size?: number;
    source?: number;
    ordering?: string;
    search?: string;
  }): Promise<ApiResponse<Article>> {
    const response: AxiosResponse<ApiResponse<Article>> = await this.api.get('/news/', { params });
    return response.data;
  }

  async getArticle(id: number): Promise<ArticleDetail> {
    const response: AxiosResponse<ArticleDetail> = await this.api.get(`/news/${id}/`);
    return response.data;
  }

  async getArticleSummary(id: number): Promise<ArticleSummary> {
    const response: AxiosResponse<ArticleSummary> = await this.api.get(`/news/${id}/summary/`);
    return response.data;
  }

  // News Sources API
  async getSources(): Promise<NewsSource[]> {
    const response: AxiosResponse<ApiResponse<NewsSource>> = await this.api.get('/sources/');
    return response.data.results;
  }

  async getSource(id: number): Promise<NewsSource> {
    const response: AxiosResponse<NewsSource> = await this.api.get(`/sources/${id}/`);
    return response.data;
  }

  // Search API
  async searchArticles(searchRequest: SearchRequest): Promise<SearchResponse> {
    const response: AxiosResponse<SearchResponse> = await this.api.post('/search/', searchRequest);
    return response.data;
  }

  // Market Data API
  async getMarketData(): Promise<MarketData> {
    try {
      console.log('Fetching market data...');
      const response: AxiosResponse<MarketData> = await this.api.get('/market-indices/');
      console.log('Market data response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      throw error;
    }
  }

  // Scraping API
  async getScrapingStatus(): Promise<ScrapingStatus> {
    const response: AxiosResponse<ScrapingStatus> = await this.api.get('/scraping-status/');
    return response.data;
  }

  async triggerScraping(source?: string): Promise<ScrapingResult> {
    const data = source ? { source } : {};
    const response: AxiosResponse<ScrapingResult> = await this.api.post('/scrape/', data);
    return response.data;
  }

  async controlScraping(action: 'start' | 'stop'): Promise<{ success: boolean; message: string }> {
    const response: AxiosResponse<{ success: boolean; message: string }> = await this.api.post('/scraping-status/', { action });
    return response.data;
  }

  // Health Check API
  async getHealthStatus(): Promise<{ status: string; timestamp: string }> {
    const response: AxiosResponse<{ status: string; timestamp: string }> = await this.api.get('/health/');
    return response.data;
  }
}

// Create and export a singleton instance
export const apiService = new ApiService(); 