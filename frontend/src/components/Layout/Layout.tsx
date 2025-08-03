import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Container,
  useTheme,
  useMediaQuery,
  Button,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store';
import { toggleSidebar, toggleTheme } from '../../store/slices/uiSlice';
import MarketIndices from '../MarketIndices/MarketIndices';

interface LayoutProps {
  children: React.ReactNode;
}

const rightSidebarWidth = 320;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  
  const { sidebarOpen, theme: appTheme } = useAppSelector((state) => state.ui);

  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
  ];

  const handleDrawerToggle = () => {
    dispatch(toggleSidebar());
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      dispatch(toggleSidebar());
    }
  };

  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };

  const mobileDrawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Stock News
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            onClick={() => handleNavigation(item.path)}
            sx={{
              bgcolor: location.pathname === item.path ? 'action.selected' : 'transparent',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top App Bar with Navigation */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {/* Mobile menu button */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          {/* Logo/Brand */}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Stock News Aggregator
          </Typography>

          {/* Desktop Navigation Menu */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
            {menuItems.map((item) => (
              <Button
                key={item.text}
                color="inherit"
                startIcon={item.icon}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  bgcolor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                {item.text}
              </Button>
            ))}
          </Box>

          {/* Theme Toggle */}
          <IconButton color="inherit" onClick={handleThemeToggle} sx={{ ml: 2 }}>
            {appTheme === 'dark' ? <LightIcon /> : <DarkIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Mobile Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: 0 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={sidebarOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
          }}
        >
          {mobileDrawer}
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box sx={{ display: 'flex', flex: 1, pt: '64px' }}>
        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: '100%',
            mr: { md: `${rightSidebarWidth}px` },
          }}
        >
          <Container maxWidth="xl">
            {children}
          </Container>
        </Box>

        {/* Right Sidebar - Market Indices */}
        <Box
          component="aside"
          sx={{
            width: { md: rightSidebarWidth },
            display: { xs: 'none', md: 'block' },
            position: 'fixed',
            right: 0,
            top: '64px',
            height: 'calc(100vh - 64px)',
            overflow: 'hidden',
            bgcolor: 'background.paper',
            borderLeft: '1px solid',
            borderColor: 'divider',
            zIndex: (theme) => theme.zIndex.drawer,
          }}
        >
          <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 1 }}>
              Market Overview
            </Typography>
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              <MarketIndices />
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Layout; 