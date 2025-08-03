#!/bin/bash

# Stock News Aggregator Development Server
# This script starts both backend and frontend servers concurrently

echo "🚀 Starting Stock News Aggregator Development Servers..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Stopping all servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📡 Starting Django Backend (http://localhost:8000)..."
cd backend && python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting React Frontend (http://localhost:3001)..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "✅ Both servers are starting..."
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Admin Panel: http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait 