import React from 'react';
import {
  Typography,
  Box,
  IconButton,
  Chip,
  Skeleton,
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { MarketData } from '../../types';

const MarketIndices: React.FC = () => {
  const {
    data: marketData,
    isLoading,
    error,
    refetch,
  } = useQuery<MarketData>({
    queryKey: ['marketData'],
    queryFn: () => apiService.getMarketData(),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  console.log('MarketIndices render:', { marketData, isLoading, error });

  const handleRefresh = () => {
    refetch();
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'success' : 'error';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? '↗' : '↘';
  };

  if (error) {
    return (
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography variant="caption" color="error">
            Failed to load market data
          </Typography>
          <IconButton onClick={handleRefresh} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
        <Box display="flex" alignItems="center" gap={0.5}>
          {marketData && (
            <Typography variant="caption" color="text.secondary">
              {new Date(marketData.last_updated).toLocaleTimeString()}
            </Typography>
          )}
        </Box>
        <IconButton
          onClick={handleRefresh}
          disabled={isLoading}
          size="small"
          aria-label="refresh market data"
        >
          <RefreshIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Market Data */}
      {isLoading ? (
        // Loading skeletons - more compact
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Box key={index} mb={1}>
              <Skeleton variant="text" width="50%" height={16} />
              <Skeleton variant="text" width="30%" height={14} />
            </Box>
          ))}
        </Box>
      ) : marketData ? (
        // Market data - compact layout
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          {marketData.indices.map((index) => (
            <Box 
              key={index.name} 
              mb={1} 
              p={1} 
              sx={{ 
                border: '1px solid', 
                borderColor: 'divider', 
                borderRadius: 1,
                bgcolor: 'background.paper',
                '&:last-child': { mb: 0 }
              }}
            >
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                  {index.name}
                </Typography>
                <Chip
                  label={`${getChangeIcon(index.change)} ${index.change_percentage.toFixed(1)}%`}
                  color={getChangeColor(index.change) as any}
                  size="small"
                  variant="outlined"
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              </Box>
              <Typography variant="body2" component="div" sx={{ fontWeight: 600, mb: 0.5 }}>
                {formatNumber(index.value)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatNumber(Math.abs(index.change))} ({index.change_percentage.toFixed(1)}%)
              </Typography>
            </Box>
          ))}
        </Box>
      ) : (
        // No data
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="caption" color="text.secondary" align="center">
            No market data available
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default MarketIndices; 