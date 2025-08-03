import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { MarketData } from '../../types';
import { apiService } from '../../services/api';

// Async thunks
export const fetchMarketData = createAsyncThunk(
  'market/fetchMarketData',
  async () => {
    const response = await apiService.getMarketData();
    return response;
  }
);

// Initial state
interface MarketState {
  data: MarketData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: MarketState = {
  data: null,
  loading: false,
  error: null,
  lastUpdated: null,
};

// Slice
const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearMarketData: (state) => {
      state.data = null;
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMarketData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMarketData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchMarketData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch market data';
      });
  },
});

export const { clearError, clearMarketData } = marketSlice.actions;

export default marketSlice.reducer; 