import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Button,
  Breadcrumbs,
  Link,
  Alert,
  Container,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Stack
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import SourceIcon from '@mui/icons-material/Source';
import SummarizeIcon from '@mui/icons-material/Summarize';
import LaunchIcon from '@mui/icons-material/Launch';
import axios from 'axios';

const ArticleView = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const article = location.state?.article;
  const [summary, setSummary] = useState('');
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get the article URL, handling both cases
  const articleUrl = article?.URL || article?.url;
  
  // Debug logging
  console.log('Article data:', article);
  console.log('Article URL:', articleUrl);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Date not available';
    }
  };

  const handleSummarize = async () => {
    if (!articleUrl) {
      setError('No URL available for this article');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8080/api/summarize', {
        url: articleUrl
      });
      setSummary(response.data.summary);
      setSummaryOpen(true);
    } catch (err) {
      console.error('Summarize error:', err);
      setError(err.response?.data?.error || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  const handleVisitSite = () => {
    if (articleUrl) {
      window.open(articleUrl, '_blank', 'noopener,noreferrer');
    } else {
      setError('No URL available for this article');
    }
  };

  if (!article) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/')}>
              Back to News
            </Button>
          }
        >
          Article not found. The article might have been removed or the link is invalid.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link
            component="button"
            variant="body2"
            onClick={() => {
              const fromState = location.state?.from;
              const params = new URLSearchParams();
              if (fromState) {
                if (fromState.page > 1) params.set('page', fromState.page.toString());
                if (fromState.pageSize !== 10) params.set('pageSize', fromState.pageSize.toString());
                if (fromState.search) params.set('search', fromState.search);
              }
              navigate(`/?${params.toString()}`);
            }}
            underline="hover"
            color="inherit"
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <ArrowBackIcon sx={{ mr: 0.5, fontSize: 20 }} />
            Back to News
          </Link>
          <Typography color="text.primary">Article</Typography>
        </Breadcrumbs>

        <Paper sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Typography 
              variant="h4" 
              sx={{ 
                fontWeight: 600,
                lineHeight: 1.3,
                flex: 1,
                mr: 2
              }}
            >
              {article.title}
            </Typography>
            <Button
              variant="outlined"
              startIcon={<SummarizeIcon />}
              onClick={handleSummarize}
              disabled={loading}
              sx={{ minWidth: 120 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Summarize'}
            </Button>
          </Box>

          <Box sx={{ 
            display: 'flex', 
            gap: 2, 
            mb: 4,
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            <Chip
              icon={<SourceIcon />}
              label={article.source?.name || article.source || 'Unknown Source'}
              variant="outlined"
              size="small"
            />
            <Chip
              icon={<AccessTimeIcon />}
              label={formatDate(article.publishedAt)}
              variant="outlined"
              size="small"
            />
          </Box>

          {article.imageURL && (
            <Box 
              sx={{ 
                width: '100%',
                height: { xs: '200px', sm: '300px', md: '400px' },
                position: 'relative',
                mb: 4,
                borderRadius: 2,
                overflow: 'hidden'
              }}
            >
              <Box
                component="img"
                src={article.imageURL}
                alt={article.title}
                sx={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            </Box>
          )}

          {article.description && (
            <Typography 
              variant="subtitle1" 
              sx={{ 
                mb: 3,
                fontWeight: 500,
                lineHeight: 1.6,
                color: 'text.primary'
              }}
            >
              {article.description}
            </Typography>
          )}

          <Divider sx={{ my: 3 }} />

          {article.content && (
            <Typography 
              variant="body1" 
              sx={{ 
                lineHeight: 1.8,
                color: 'text.primary'
              }}
            >
              {article.content}
            </Typography>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 3 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ 
            mt: 4, 
            pt: 3, 
            borderTop: 1, 
            borderColor: 'divider',
            display: 'flex',
            justifyContent: 'flex-start'
          }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<LaunchIcon />}
              onClick={handleVisitSite}
              sx={{ 
                minWidth: 200,
                py: 1.5,
                borderRadius: 2,
                boxShadow: 2,
                '&:hover': {
                  boxShadow: 4
                }
              }}
            >
              Read Full Article
            </Button>
          </Box>
        </Paper>
      </Box>

      <Dialog
        open={summaryOpen}
        onClose={() => setSummaryOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Article Summary
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
            {summary}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSummaryOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ArticleView; 