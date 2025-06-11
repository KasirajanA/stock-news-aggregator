# Stock News Aggregator

A real-time stock market news aggregator built with React and Go, featuring news from Livemint and Economic Times.

## Project Structure

```
stock_news_aggregator/
├── frontend/               # React frontend application
│   ├── src/               # Source files
│   │   ├── components/    # React components
│   │   └── App.jsx       # Main App component
│   ├── public/            # Static files
│   ├── package.json       # Frontend dependencies
│   └── vite.config.js     # Vite configuration
│
└── backend/               # Go backend application
    ├── models/            # Data models
    ├── services/          # Business logic and services
    └── main.go           # Entry point
```

## Features

- Real-time market indices tracking
- News aggregation from multiple sources
- Clean, modern UI with Material-UI components
- Responsive design for all devices
- Real-time data updates

## Prerequisites

- Node.js v18 or higher
- Go 1.20 or higher
- npm or yarn package manager

## Setup and Installation

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Go dependencies:
   ```bash
   go mod tidy
   ```

3. Run the server:
   ```bash
   go run main.go
   ```
   The backend API will be available at http://localhost:8080

## API Endpoints

- GET `/api/market-indices` - Get current market indices
- GET `/api/news` - Get aggregated news from all sources

## Technologies Used

- Frontend:
  - React
  - Material-UI
  - Vite
  - Axios

- Backend:
  - Go
  - Gin Framework
  - Colly (Web Scraping)

## Development

Both servers (frontend and backend) need to be running for full functionality. Run them in separate terminal windows following the setup instructions above.
