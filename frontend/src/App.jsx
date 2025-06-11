import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Container, CssBaseline, Box, Paper } from '@mui/material';
import NewsList from './components/NewsList';
import ArticleView from './components/ArticleView';
import MarketIndices from './components/MarketIndices';

// Wrapper component to handle layout based on route
const Layout = () => {
  const location = useLocation();
  const isArticlePage = location.pathname.startsWith('/article');

  if (isArticlePage) {
    return (
      <Box sx={{ width: '100%', minHeight: '100vh' }}>
        <ArticleView />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      gap: 3,
      minHeight: '100vh',
      position: 'relative'
    }}>
      {/* News List - 70% width */}
      <Box sx={{ 
        flex: '0 0 70%',
        maxWidth: '70%',
        position: 'relative'
      }}>
        <NewsList />
      </Box>

      {/* Market Indices - 30% width */}
      <Box sx={{ 
        flex: '0 0 28%',
        maxWidth: '28%',
        position: 'sticky',
        top: 24,
        alignSelf: 'flex-start',
        height: 'fit-content'
      }}>
        <Paper elevation={0} sx={{ p: 2, backgroundColor: 'background.paper' }}>
          <MarketIndices />
        </Paper>
      </Box>
    </Box>
  );
};

function App() {
  return (
    <Router>
      <CssBaseline />
      <Container 
        maxWidth="xl" 
        sx={{ 
          py: 3,
          minHeight: '100vh',
          backgroundColor: '#f5f5f5'
        }}
      >
        <Routes>
          <Route path="/*" element={<Layout />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
