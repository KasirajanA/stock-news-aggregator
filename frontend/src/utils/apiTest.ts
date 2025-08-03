import { apiService } from '../services/api';

export const testApiIntegration = async () => {
  console.log('🧪 Testing API Integration...');
  
  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const health = await apiService.getHealthStatus();
    console.log('✅ Health check passed:', health);
    
    // Test sources endpoint
    console.log('2. Testing sources endpoint...');
    const sources = await apiService.getSources();
    console.log('✅ Sources loaded:', sources.length, 'sources');
    
    // Test articles endpoint
    console.log('3. Testing articles endpoint...');
    const articles = await apiService.getArticles({ page: 1, page_size: 5 });
    console.log('✅ Articles loaded:', articles.results.length, 'articles');
    
    // Test market data endpoint
    console.log('4. Testing market data endpoint...');
    const marketData = await apiService.getMarketData();
    console.log('✅ Market data loaded:', marketData.indices.length, 'indices');
    
    console.log('🎉 All API tests passed!');
    return true;
  } catch (error) {
    console.error('❌ API test failed:', error);
    return false;
  }
}; 