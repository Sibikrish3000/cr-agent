#!/bin/bash

echo "========================================"
echo " Multi-Agent AI System - Startup"
echo "========================================"
echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

echo "Starting Backend Server..."
uv run uvicorn main:app --reload &
BACKEND_PID=$!
sleep 3

echo "Starting Frontend Development Server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo " Services Started!"
echo "========================================"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
