import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Skeleton,
  Pagination,
  Grid,
  Alert,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import {
  fetchArticles,
  fetchSources,
  setFilters,
  clearFilters,
} from '../store/slices/newsSlice';
import { Article } from '../types';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const {
    articles,
    sources,
    loading,
    error,
    pagination,
    filters,
  } = useAppSelector((state) => state.news);

  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [pageSize, setPageSize] = useState(20);

  useEffect(() => {
    // Fetch sources on component mount
    dispatch(fetchSources());
  }, [dispatch]);

  useEffect(() => {
    // Fetch articles when filters, search, page, or pageSize changes
    const params = {
      page,
      page_size: pageSize,
      source: filters.source,
      ordering: filters.ordering || '-published_at',
      search: searchQuery || undefined,
    };
    dispatch(fetchArticles(params));
  }, [dispatch, page, pageSize, filters, searchQuery]);

  const handleSourceFilter = (sourceId: number | '') => {
    dispatch(setFilters({ source: sourceId === '' ? undefined : sourceId }));
    setPage(1);
  };

  const handleOrderingFilter = (ordering: string) => {
    dispatch(setFilters({ ordering }));
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setPage(1);
  };

  const handlePageSizeChange = (event: any, child?: React.ReactNode) => {
    setPageSize(event.target.value as number);
    setPage(1);
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

  const renderArticleCard = (article: Article) => (
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
      <Box mb={3}>
        <Typography variant="h4" component="h1">
          Latest News
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Box mb={3}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="flex-end">
          <TextField
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
            sx={{ minWidth: 300 }}
            size="small"
          />

          <FormControl sx={{ minWidth: 200 }} size="small">
            <InputLabel>Source</InputLabel>
            <Select
              value={filters.source || ''}
              label="Source"
              onChange={(e) => handleSourceFilter(e.target.value as number | '')}
            >
              <MenuItem value="">All Sources</MenuItem>
              {sources.map((source) => (
                <MenuItem key={source.id} value={source.id}>
                  {source.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }} size="small">
            <InputLabel>Sort By</InputLabel>
            <Select
              value={filters.ordering || '-published_at'}
              label="Sort By"
              onChange={(e) => handleOrderingFilter(e.target.value)}
            >
              <MenuItem value="-published_at">Latest First</MenuItem>
              <MenuItem value="published_at">Oldest First</MenuItem>
              <MenuItem value="-created_at">Recently Added</MenuItem>
              <MenuItem value="title">Title A-Z</MenuItem>
              <MenuItem value="-title">Title Z-A</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Per Page</InputLabel>
            <Select
              value={pageSize}
              label="Per Page"
              onChange={handlePageSizeChange}
            >
              <MenuItem value={10}>10 articles</MenuItem>
              <MenuItem value={20}>20 articles</MenuItem>
              <MenuItem value={50}>50 articles</MenuItem>
              <MenuItem value={100}>100 articles</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            onClick={() => {
              dispatch(clearFilters());
              setSearchQuery('');
              setPageSize(20);
            }}
            disabled={!filters.source && !filters.ordering && !searchQuery && pageSize === 20}
            size="small"
          >
            Clear All
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Info */}
      {!loading && (
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="body2" color="text.secondary">
            Showing {articles.length} of {pagination.totalCount} articles
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Page {page} of {Math.ceil(pagination.totalCount / pageSize)}
          </Typography>
        </Box>
      )}

      {/* Articles Grid */}
      <Grid container spacing={3}>
        {loading
          ? Array.from({ length: pageSize }).map((_, index) => renderSkeleton())
          : articles.map(renderArticleCard)}
      </Grid>

      {/* Pagination */}
      {pagination.totalCount > pageSize && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination
            count={Math.ceil(pagination.totalCount / pageSize)}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      )}

      {/* No Articles */}
      {!loading && articles.length === 0 && !error && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No articles found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your filters or check back later for new content.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default HomePage; 