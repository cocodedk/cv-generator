#!/bin/bash

# CV Generator - Development Startup Script
# This script starts the backend/Neo4j in Docker and the frontend locally

set -e

echo "🚀 Starting CV Generator Development Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# PID file for build watcher
BUILD_WATCHER_PID_FILE="$PROJECT_ROOT/.build-watcher.pid"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"

    # Stop build watcher if running
    if [ -f "$BUILD_WATCHER_PID_FILE" ]; then
        BUILD_WATCHER_PID=$(cat "$BUILD_WATCHER_PID_FILE")
        if ps -p "$BUILD_WATCHER_PID" > /dev/null 2>&1; then
            echo -e "${BLUE}Stopping build watcher...${NC}"
            kill "$BUILD_WATCHER_PID" 2>/dev/null || true
        fi
        rm -f "$BUILD_WATCHER_PID_FILE"
    fi

    docker-compose down
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Start backend and Neo4j services
echo -e "${BLUE}📦 Starting Docker services (backend + Neo4j)...${NC}"
docker-compose up -d

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${YELLOW}⚠️  Backend health check timeout, but continuing anyway...${NC}"
fi

# Ensure frontend dependencies are installed
if [ ! -d "node_modules" ] || [ ! -e "node_modules/.bin/cross-env" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Start build watcher in background
echo -e "${BLUE}🔨 Starting build watcher...${NC}"
npm run build:watch > /dev/null 2>&1 &
BUILD_WATCHER_PID=$!
echo "$BUILD_WATCHER_PID" > "$BUILD_WATCHER_PID_FILE"
echo -e "${GREEN}✅ Build watcher started (PID: $BUILD_WATCHER_PID)${NC}"

# Start frontend dev server
echo ""
echo -e "${GREEN}✅ Docker services are running!${NC}"
echo -e "${BLUE}🌐 Starting frontend dev server...${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   CV Generator is running!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "Frontend (with HMR): ${BLUE}http://localhost:5173${NC}"
echo -e "Backend API:         ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs:            ${BLUE}http://localhost:8000/docs${NC}"
echo -e "Neo4j Browser:       ${BLUE}http://localhost:7474${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Start frontend (this will block)
npm run dev
