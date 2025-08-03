# Stock News Aggregator

A comprehensive stock news aggregator with live market data, AI-powered summaries, and real-time news from Indian financial sources.

## 🚀 Quick Start

### Option 1: Using npm (Recommended)
```bash
# Install all dependencies
npm run install-all

# Start both backend and frontend servers
npm run dev
```

### Option 2: Using shell script
```bash
# Make script executable (first time only)
chmod +x start-dev.sh

# Start both servers
./start-dev.sh
```

### Option 3: Manual start
```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Frontend
cd frontend
npm start
```

## 📱 Access Points

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 🛠️ Available Commands

### Development
```bash
npm run dev              # Start both servers
npm run backend          # Start only backend
npm run frontend         # Start only frontend
```

### Database & Setup
```bash
npm run migrate          # Run database migrations
npm run makemigrations  # Create new migrations
npm run shell           # Open Django shell
npm run superuser       # Create admin user
```

### Build & Test
```bash
npm run build           # Build frontend for production
npm run test            # Run backend tests
npm run install-all     # Install all dependencies
```

## 🏗️ Project Structure

```
stock-news-aggregator/
├── backend/                 # Django API
│   ├── news/               # News scraping & management
│   ├── market_data/        # Live market data
│   └── stock_news_aggregator/  # Django settings
├── frontend/               # React TypeScript app
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── store/          # Redux state management
│   └── public/             # Static assets
├── package.json            # Root package.json
├── start-dev.sh           # Shell script for development
└── README.md              # This file
```

## 🌟 Features

### 📰 News Aggregation
- **7 Indian News Sources**: LiveMint, Economic Times, MoneyControl, Business Line, Business Standard, Business Today, India Today
- **RSS & Web Scraping**: Robust scraping with fallback mechanisms
- **Real-time Updates**: Automatic scraping every 5 minutes
- **Search & Filter**: Advanced search with source filtering

### 🤖 AI Summarization
- **TextRank Algorithm**: Free, offline summarization using NLTK
- **Smart Caching**: Summaries cached for reuse
- **Popup Display**: Clean summary interface in article details

### 📊 Live Market Data
- **NSE Integration**: Real-time data from NSE India
- **Commodities**: Gold, Silver prices
- **Currency**: USD/INR exchange rate
- **Smart Caching**: 5-minute cache with fallback data
- **Market Hours**: Shows last live data when market is closed

### 🎨 Modern UI
- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Theme**: Toggle between themes
- **Compact Layout**: Market overview fits without scrolling
- **Material-UI**: Professional component library

## 🔧 Technology Stack

### Backend
- **Django 4.2**: Python web framework
- **Django REST Framework**: API development
- **SQLite**: Database (can be upgraded to PostgreSQL)
- **NLTK**: Text summarization
- **Requests**: HTTP client for scraping
- **BeautifulSoup**: HTML parsing

### Frontend
- **React 18**: JavaScript library
- **TypeScript**: Type safety
- **Material-UI v7**: Component library
- **Redux Toolkit**: State management
- **React Query**: Data fetching
- **React Router**: Navigation

## 📈 Market Data Sources

- **NSE India**: Live stock indices (NIFTY 50, SENSEX, BANK NIFTY)
- **MCX**: Commodity prices (Gold, Silver)
- **RBI**: Currency exchange rates (USD/INR)
- **Fallback Data**: Realistic mock data when APIs are unavailable

## 🚀 Deployment

### Production Build
```bash
# Build frontend
npm run build

# Collect static files
npm run collectstatic

# Run with production server (gunicorn, uvicorn, etc.)
```

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000/api/v1

# Backend (settings.py)
DEBUG=False
ALLOWED_HOSTS=['your-domain.com']
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for Indian financial markets**
