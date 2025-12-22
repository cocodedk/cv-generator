#!/bin/bash

# CV Generator - Development Stop Script
# Stops all Docker services and build watcher

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping CV Generator services...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# PID file for build watcher
BUILD_WATCHER_PID_FILE="$PROJECT_ROOT/.build-watcher.pid"

# Stop build watcher if running
if [ -f "$BUILD_WATCHER_PID_FILE" ]; then
    BUILD_WATCHER_PID=$(cat "$BUILD_WATCHER_PID_FILE")
    if ps -p "$BUILD_WATCHER_PID" > /dev/null 2>&1; then
        echo -e "${BLUE}Stopping build watcher (PID: $BUILD_WATCHER_PID)...${NC}"
        kill "$BUILD_WATCHER_PID" 2>/dev/null || true
        echo -e "${GREEN}✅ Build watcher stopped${NC}"
    fi
    rm -f "$BUILD_WATCHER_PID_FILE"
fi

docker-compose down

echo -e "${GREEN}✅ All services stopped!${NC}"
