import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  CardActionArea,
  Skeleton,
  Alert,
  Paper,
  TextField,
  InputAdornment,
  Pagination,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';

const NewsList = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Initialize state from URL parameters
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(parseInt(searchParams.get('page')) || 1);
  const [pageSize, setPageSize] = useState(parseInt(searchParams.get('pageSize')) || 10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Update URL when page, pageSize, or search changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (page > 1) params.set('page', page.toString());
    if (pageSize !== 10) params.set('pageSize', pageSize.toString());
    if (searchQuery) params.set('search', searchQuery);
    setSearchParams(params);
  }, [page, pageSize, searchQuery, setSearchParams]);

  const fetchNews = useCallback(async () => {
    console.log(`Fetching news for page ${page}, pageSize ${pageSize}, search: "${searchQuery}"`);
    try {
      setLoading(true);
      setError(null);

      const axiosConfig = {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        params: {
          page,
          pageSize,
          ...(searchQuery.trim() && { search: searchQuery.trim() })
        }
      };

      const response = await axios.get(`${API_BASE_URL}/api/news/db`, axiosConfig);
      
      if (!response.data) {
        throw new Error('Invalid data format received from server');
      }

      const { articles, totalPages: totalPagesFromServer, totalCount: totalCountFromServer } = response.data;
      
      console.log(`Received ${articles.length} articles from API (page ${page}/${totalPagesFromServer}, total: ${totalCountFromServer})`);
      
      setNews(articles);
      setTotalPages(totalPagesFromServer);
      setTotalCount(totalCountFromServer);
    } catch (err) {
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        request: err.request,
        config: err.config
      });

      let errorMessage = 'Failed to load news articles.';
      if (err.response) {
        errorMessage = `Server error: ${err.response.status} - ${err.response.data?.message || err.message}`;
      } else if (err.request) {
        errorMessage = 'Could not reach the news server. Please check your connection.';
      } else {
        errorMessage = `Error setting up request: ${err.message}`;
      }

      setError(errorMessage);
      setNews([]);
      setTotalPages(1);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchQuery]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      fetchNews();
    }, 300); // Debounce search by 300ms

    return () => clearTimeout(debounceTimer);
  }, [fetchNews]);

  const handleArticleClick = (article) => {
    navigate(`/article/${article.id || ''}`, { 
      state: { 
        article,
        from: {
          page,
          pageSize,
          search: searchQuery
        }
      } 
    });
  };

  const handleSearchChange = (event) => {
    const newQuery = event.target.value;
    console.log(`Search query changed to: "${newQuery}"`);
    setSearchQuery(newQuery);
    setPage(1); // Reset to first page on search
  };

  const handlePageChange = (event, newPage) => {
    console.log(`Changing to page ${newPage}`);
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePageSizeChange = (event) => {
    const newSize = event.target.value;
    console.log(`Changing page size to ${newSize}`);
    setPageSize(newSize);
    setPage(1); // Reset to first page when changing page size
  };

  const renderNewsCards = () => {
    if (loading) {
      return Array(pageSize).fill(null).map((_, index) => (
        <Card key={`skeleton-${index}`} sx={{ mb: 2 }}>
          <CardContent>
            <Skeleton variant="text" width="60%" height={32} />
            <Skeleton variant="text" width="40%" height={24} sx={{ mb: 1 }} />
            <Skeleton variant="text" width="100%" height={20} />
            <Skeleton variant="text" width="100%" height={20} />
          </CardContent>
        </Card>
      ));
    }

    if (!Array.isArray(news) || news.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No news articles available at the moment.
          </Typography>
        </Box>
      );
    }

    return news.map((article, index) => (
      <Card 
        key={article.id || index} 
        sx={{ 
          mb: 2,
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 3
          }
        }}
      >
        <CardActionArea onClick={() => handleArticleClick(article)}>
          <CardContent>
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontSize: '1.1rem',
                fontWeight: 500,
                lineHeight: 1.3
              }}
            >
              {article.title || 'No Title'}
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              gutterBottom
              sx={{ mb: 1 }}
            >
              {article.source?.name || article.source || 'Unknown Source'} • {
                article.publishedAt 
                  ? new Date(article.publishedAt).toLocaleString()
                  : 'No Date'
              }
            </Typography>
            <Typography 
              variant="body2"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                lineHeight: 1.5
              }}
            >
              {article.description || 'No description available'}
            </Typography>
          </CardContent>
        </CardActionArea>
      </Card>
    ));
  };

  return (
    <Box sx={{ position: 'relative', minHeight: '100vh' }}>
      <Typography 
        variant="h4" 
        component="h1" 
        sx={{ 
          mb: 3, 
          fontWeight: 600,
          color: 'primary.main',
          borderBottom: 2,
          borderColor: 'primary.main',
          pb: 1,
          display: 'inline-block'
        }}
      >
        Indian Market News
      </Typography>

      <Paper 
        elevation={0} 
        sx={{ 
          p: 2, 
          mb: 3, 
          backgroundColor: 'background.paper',
          display: 'flex',
          gap: 2,
          alignItems: 'center'
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search articles..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flex: 1 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel id="page-size-label">Per Page</InputLabel>
          <Select
            labelId="page-size-label"
            value={pageSize}
            label="Per Page"
            onChange={handlePageSizeChange}
          >
            <MenuItem value={10}>10</MenuItem>
            <MenuItem value={20}>20</MenuItem>
            <MenuItem value={50}>50</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ position: 'relative' }}>
        {renderNewsCards()}
      </Box>

      {!loading && totalPages > 0 && (
        <Stack 
          direction="row" 
          spacing={2} 
          justifyContent="center"
          alignItems="center"
          sx={{ mt: 4 }}
        >
          <Typography variant="body2" color="text.secondary">
            {`${totalCount} articles found`}
          </Typography>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Stack>
      )}
    </Box>
  );
};

export default NewsList; 