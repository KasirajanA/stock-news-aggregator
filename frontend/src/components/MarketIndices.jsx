import React, { useState, useEffect } from 'react';
import { Box, Typography, Skeleton, Paper, Alert, IconButton } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import RefreshIcon from '@mui/icons-material/Refresh';
import axios from 'axios';

const MarketIndices = () => {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchIndices = async (isManualRefresh = false) => {
    try {
      if (!isManualRefresh) {
        setLoading(true);
      }
      const response = await axios.get('http://localhost:8080/api/market-indices', {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true
      });
      
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        // Process the data to ensure we have valid numbers
        const processedIndices = response.data.map(index => ({
          ...index,
          price: typeof index.price === 'number' ? index.price : null,
          change: typeof index.change === 'number' ? index.change : 0,
          changePerc: typeof index.changePerc === 'number' ? index.changePerc : 0,
          isHistorical: index.isDelayed || false
        }));
        setIndices(processedIndices);
        setError(null);
        setLastUpdated(new Date());
      } else {
        throw new Error('Invalid or empty data received');
      }
    } catch (error) {
      console.error('Error fetching market indices:', error);
      
      let errorMessage = 'Failed to fetch market data';
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response?.data?.details) {
        errorMessage = error.response.data.details;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndices();
    return () => {};
  }, []);

  const handleRefresh = () => {
    fetchIndices(true);
  };

  if (loading && !indices.length) {
    return (
      <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
        <Skeleton variant="rounded" height={80} />
        <Skeleton variant="rounded" height={80} />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2" color="text.secondary">
          {lastUpdated ? `Last updated: ${lastUpdated.toLocaleTimeString()}` : ''}
          {lastUpdated && (
            <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
              (Click refresh to update)
            </Typography>
          )}
        </Typography>
        <IconButton 
          onClick={handleRefresh} 
          size="small" 
          disabled={loading}
          sx={{ ml: 1 }}
        >
          <RefreshIcon />
        </IconButton>
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 2,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
        >
          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
            Unable to load market data
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            {error}
          </Typography>
        </Alert>
      )}

      {indices.map((index) => (
        <Paper
          key={index.symbol}
          sx={{
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'background.paper',
            opacity: loading ? 0.7 : 1,
            transition: 'opacity 0.2s',
          }}
          elevation={0}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              {index.name || 'Unknown Index'}
            </Typography>
            {index.isDelayed && (
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'warning.main',
                  backgroundColor: 'warning.lighter',
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  fontSize: '0.7rem'
                }}
              >
                Delayed
              </Typography>
            )}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {index.price !== null
                ? index.price.toLocaleString('en-IN', { 
                    maximumFractionDigits: 2,
                    minimumFractionDigits: 2 
                  })
                : 'N/A'
              }
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {index.change >= 0 ? (
                <TrendingUpIcon sx={{ color: 'success.main', fontSize: '1rem', mr: 0.5 }} />
              ) : (
                <TrendingDownIcon sx={{ color: 'error.main', fontSize: '1rem', mr: 0.5 }} />
              )}
              <Typography
                variant="body2"
                sx={{
                  color: index.change >= 0 ? 'success.main' : 'error.main',
                  fontWeight: 'medium',
                }}
              >
                {index.change >= 0 ? '+' : ''}
                {index.change.toFixed(2)}
              </Typography>
            </Box>
            <Typography
              variant="body2"
              sx={{
                color: index.change >= 0 ? 'success.main' : 'error.main',
                fontWeight: 'medium',
              }}
            >
              ({(index.changePerc >= 0 ? '+' : '') + index.changePerc.toFixed(2)}%)
            </Typography>
          </Box>
          {index.isHistorical && (
            <Typography 
              variant="caption" 
              color="text.secondary" 
              sx={{ mt: 1 }}
            >
              Last trading day's closing values
            </Typography>
          )}
        </Paper>
      ))}
    </Box>
  );
};

export default MarketIndices; 