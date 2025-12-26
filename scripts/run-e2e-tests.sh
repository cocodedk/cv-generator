#!/bin/bash

# CV Generator - Run E2E Tests
# This script runs Playwright E2E tests
#
# Usage:
#   ./scripts/run-e2e-tests.sh           # Run E2E tests
#   ./scripts/run-e2e-tests.sh --headed  # Run with visible browser

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Parse command-line arguments
HEADED_MODE=0

for arg in "$@"; do
    case $arg in
        --headed)
            HEADED_MODE=1
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🌐 Running E2E tests (Playwright)...${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

# Check if Playwright is installed
if [ ! -f "node_modules/.bin/playwright" ]; then
    echo -e "${YELLOW}⚠️  Playwright not found. Installing...${NC}"
    npm install -D @playwright/test
    npx playwright install --with-deps chromium
fi

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend is not running on http://localhost:8000${NC}"
    echo -e "${YELLOW}   E2E tests require the backend to be running.${NC}"
    echo -e "${YELLOW}   Start it with: npm run dev:full${NC}"
    exit 2  # Exit code 2 for skipped (services not running)
fi

# Check if frontend is running
if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend is not running on http://localhost:5173${NC}"
    echo -e "${YELLOW}   E2E tests require the frontend to be running.${NC}"
    echo -e "${YELLOW}   Start it with: npm run dev:full${NC}"
    exit 2  # Exit code 2 for skipped (services not running)
fi

# Run E2E tests
PLAYWRIGHT_ARGS=""
if [ $HEADED_MODE -eq 1 ]; then
    PLAYWRIGHT_ARGS="--headed"
    echo -e "${BLUE}   Running in headed mode (browser will be visible)${NC}"
fi

if npx playwright test $PLAYWRIGHT_ARGS; then
    echo -e "${GREEN}✅ E2E tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ E2E tests failed!${NC}"
    exit 1
fi
