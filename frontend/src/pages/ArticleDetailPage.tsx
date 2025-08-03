import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Divider,
  Skeleton,
  Alert,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  OpenInNew as OpenInNewIcon,
  Summarize as SummarizeIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../store';
import { fetchArticle, fetchArticleSummary } from '../store/slices/newsSlice';

const ArticleDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentArticle, loading, error, sources } = useAppSelector((state) => state.news);
  const [summaryDialogOpen, setSummaryDialogOpen] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    if (id) {
      dispatch(fetchArticle(parseInt(id)));
    }
  }, [dispatch, id]);

  const handleBack = () => {
    navigate(-1);
  };

  const handleOpenOriginal = () => {
    if (currentArticle) {
      window.open(currentArticle.url, '_blank');
    }
  };

  const handleGetSummary = async () => {
    if (currentArticle && !currentArticle.summary) {
      setSummaryLoading(true);
      try {
        await dispatch(fetchArticleSummary(currentArticle.id)).unwrap();
        setSummaryDialogOpen(true);
      } catch (error) {
        console.error('Failed to fetch summary:', error);
      } finally {
        setSummaryLoading(false);
      }
    } else if (currentArticle?.summary) {
      setSummaryDialogOpen(true);
    }
  };

  const handleCloseSummaryDialog = () => {
    setSummaryDialogOpen(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
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
    return source?.name || 'Unknown Source';
  };

  if (loading) {
    return (
      <Box>
        <Box display="flex" alignItems="center" mb={3}>
          <Skeleton variant="circular" width={40} height={40} />
          <Skeleton variant="text" width={200} height={32} sx={{ ml: 2 }} />
        </Box>
        <Card>
          <CardContent>
            <Skeleton variant="text" width="100%" height={48} />
            <Skeleton variant="text" width="60%" height={24} />
            <Skeleton variant="text" width="100%" height={20} />
            <Skeleton variant="text" width="100%" height={20} />
            <Skeleton variant="text" width="80%" height={20} />
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!currentArticle) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        Article not found
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4" component="h1">
          Article Details
        </Typography>
      </Box>

      {/* Article Card */}
      <Card>
        <CardContent>
          {/* Article Header */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box flex={1}>
              <Typography variant="h4" component="h2" gutterBottom>
                {currentArticle.title}
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Chip
                  label={getSourceName(currentArticle.source)}
                  color="primary"
                  variant="outlined"
                />
                <Typography variant="body2" color="text.secondary">
                  Published: {formatDate(currentArticle.published_at)}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<OpenInNewIcon />}
                onClick={handleOpenOriginal}
              >
                Original
              </Button>
              <Button
                variant="contained"
                startIcon={
                  summaryLoading ? (
                    <CircularProgress size={16} color="inherit" />
                  ) : (
                    <SummarizeIcon />
                  )
                }
                onClick={handleGetSummary}
                disabled={summaryLoading}
              >
                {currentArticle.summary ? 'View Summary' : 'Get Summary'}
              </Button>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Article Meta */}
          <Box display="flex" gap={2} mb={3} flexWrap="wrap">
            {currentArticle.word_count && (
              <Typography variant="body2" color="text.secondary">
                {currentArticle.word_count} words
              </Typography>
            )}
            {currentArticle.reading_time && (
              <Typography variant="body2" color="text.secondary">
                {currentArticle.reading_time} min read
              </Typography>
            )}
            {currentArticle.summary_generated_at && (
              <Typography variant="body2" color="text.secondary">
                Summary generated: {formatDate(currentArticle.summary_generated_at)}
              </Typography>
            )}
          </Box>

          {/* Article Description */}
          <Typography variant="h6" gutterBottom>
            Description
          </Typography>
          <Typography variant="body1" paragraph>
            {currentArticle.description}
          </Typography>

          {/* Article Content */}
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom>
            Full Content
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {currentArticle.content}
          </Typography>
        </CardContent>
      </Card>

      {/* AI Summary Dialog */}
      <Dialog
        open={summaryDialogOpen}
        onClose={handleCloseSummaryDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              AI Summary
            </Typography>
            <IconButton onClick={handleCloseSummaryDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {currentArticle.summary ? (
            <Box>
              <Paper
                sx={{
                  p: 3,
                  bgcolor: 'primary.50',
                  border: '1px solid',
                  borderColor: 'primary.200',
                  borderRadius: 2,
                }}
              >
                <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                  {currentArticle.summary}
                </Typography>
              </Paper>
              {currentArticle.summary_generated_at && (
                <Box mt={2}>
                  <Typography variant="caption" color="text.secondary">
                    Generated on: {formatDate(currentArticle.summary_generated_at)}
                  </Typography>
                </Box>
              )}
            </Box>
          ) : (
            <Box textAlign="center" py={4}>
              <CircularProgress />
              <Typography variant="body1" sx={{ mt: 2 }}>
                Generating AI summary...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSummaryDialog} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ArticleDetailPage; 