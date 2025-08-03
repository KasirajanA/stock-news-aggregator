import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Skeleton,
  Alert,
  Paper,
  Grid,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store';
import { searchArticles, fetchSources, clearSearchResults } from '../store/slices/newsSlice';
import { Article } from '../types';

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const {
    searchResults,
    searchLoading,
    searchError,
    sources,
    pagination,
  } = useAppSelector((state) => state.news);

  const [query, setQuery] = useState('');
  const [selectedSource, setSelectedSource] = useState<number | ''>('');
  const [ordering, setOrdering] = useState('-published_at');
  const [page, setPage] = useState(1);

  React.useEffect(() => {
    dispatch(fetchSources());
  }, [dispatch]);

  const handleSearch = () => {
    if (query.trim()) {
      const searchRequest = {
        query: query.trim(),
        source: selectedSource === '' ? undefined : selectedSource,
        ordering,
        page,
      };
      dispatch(searchArticles(searchRequest));
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    setSelectedSource('');
    setOrdering('-published_at');
    setPage(1);
    dispatch(clearSearchResults());
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    if (query.trim()) {
      const searchRequest = {
        query: query.trim(),
        source: selectedSource === '' ? undefined : selectedSource,
        ordering,
        page: value,
      };
      dispatch(searchArticles(searchRequest));
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleArticleClick = (article: Article) => {
    navigate(`/article/${article.id}`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSourceName = (sourceId: number | { id: number; name: string }) => {
    if (typeof sourceId === 'object' && sourceId !== null) {
      return sourceId.name;
    }
    const source = sources.find((s) => s.id === sourceId);
    return source?.name || 'Unknown';
  };

  const renderSearchResult = (article: Article) => (
    <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.333333%' } }} key={article.id}>
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          cursor: 'pointer',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 4,
          },
        }}
        onClick={() => handleArticleClick(article)}
      >
        <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Chip
              label={getSourceName(article.source)}
              size="small"
              color="primary"
              variant="outlined"
            />
            <Typography variant="caption" color="text.secondary">
              {formatDate(article.published_at)}
            </Typography>
          </Box>

          <Typography variant="h6" component="h3" gutterBottom sx={{ flexGrow: 1 }}>
            {article.title}
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              mb: 2,
            }}
          >
            {article.description}
          </Typography>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" gap={1}>
              {article.word_count && (
                <Typography variant="caption" color="text.secondary">
                  {article.word_count} words
                </Typography>
              )}
              {article.reading_time && (
                <Typography variant="caption" color="text.secondary">
                  {article.reading_time} min read
                </Typography>
              )}
            </Box>
            {article.summary && (
              <Chip label="Has Summary" size="small" color="success" />
            )}
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );

  const renderSkeleton = () => (
    <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.333333%' } }}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Skeleton variant="text" width="30%" height={24} />
          <Skeleton variant="text" width="100%" height={32} />
          <Skeleton variant="text" width="100%" height={20} />
          <Skeleton variant="text" width="80%" height={20} />
          <Skeleton variant="text" width="60%" height={20} />
        </CardContent>
      </Card>
    </Grid>
  );

  return (
    <Box>
      {/* Header */}
      <Typography variant="h4" component="h1" gutterBottom>
        Search Articles
      </Typography>

      {/* Search Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid component="div" sx={{ width: { xs: '100%', md: '50%' } }}>
            <TextField
              fullWidth
              label="Search articles..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter keywords, titles, or content..."
            />
          </Grid>
          <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '25%' } }}>
            <FormControl fullWidth>
              <InputLabel>Source</InputLabel>
              <Select
                value={selectedSource}
                label="Source"
                onChange={(e) => setSelectedSource(e.target.value as number | '')}
              >
                <MenuItem value="">All Sources</MenuItem>
                {sources.map((source) => (
                  <MenuItem key={source.id} value={source.id}>
                    {source.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '25%' } }}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={ordering}
                label="Sort By"
                onChange={(e) => setOrdering(e.target.value)}
              >
                <MenuItem value="-published_at">Latest First</MenuItem>
                <MenuItem value="published_at">Oldest First</MenuItem>
                <MenuItem value="title">Title A-Z</MenuItem>
                <MenuItem value="-title">Title Z-A</MenuItem>
                <MenuItem value="-created_at">Recently Added</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '25%' } }}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={!query.trim() || searchLoading}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Alert */}
      {searchError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {searchError}
        </Alert>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Search Results ({pagination.totalCount} articles found)
            </Typography>
            <Button variant="outlined" onClick={handleClearSearch}>
              Clear Search
            </Button>
          </Box>

          <Grid container spacing={3}>
            {searchLoading
              ? Array.from({ length: 6 }).map((_, index) => renderSkeleton())
              : searchResults.map(renderSearchResult)}
          </Grid>

          {/* Pagination */}
          {pagination.totalCount > pagination.pageSize && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={Math.ceil(pagination.totalCount / pagination.pageSize)}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </Box>
      )}

      {/* No Results */}
      {!searchLoading && searchResults.length === 0 && query.trim() && !searchError && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No articles found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search terms or filters.
          </Typography>
        </Box>
      )}

      {/* Initial State */}
      {!query.trim() && searchResults.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Start your search
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enter keywords to search through all articles.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SearchPage; 