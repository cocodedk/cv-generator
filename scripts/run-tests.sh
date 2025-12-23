#!/bin/bash

# CV Generator - Run All Tests
# This script runs both backend and frontend tests

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

echo -e "${BLUE}🧪 Running CV Generator Tests...${NC}"
echo ""

# Track test results
BACKEND_PASSED=0
FRONTEND_PASSED=0

# Function to run backend tests
run_backend_tests() {
    echo -e "${BLUE}📦 Running backend tests (in Docker)...${NC}"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker is not running. Skipping backend tests.${NC}"
        echo -e "${YELLOW}   To run backend tests locally, use: npm run test:backend:local${NC}"
        return 1
    fi

    # Check if containers are running
    if ! docker-compose ps | grep -q "cv-app.*Up"; then
        echo -e "${YELLOW}⚠️  Backend container is not running. Starting it...${NC}"
        docker-compose up -d app
        sleep 5
    fi

    # Run backend tests
    if docker-compose exec -T app python -m pytest || docker-compose run --rm app python -m pytest; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
        BACKEND_PASSED=1
        return 0
    else
        echo -e "${RED}❌ Backend tests failed!${NC}"
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${BLUE}⚛️  Running frontend tests...${NC}"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
        npm install
    fi

    # Check if vitest is available
    if [ ! -f "node_modules/.bin/vitest" ]; then
        echo -e "${YELLOW}⚠️  vitest not found. Installing dependencies...${NC}"
        npm install
    fi

    # Change to frontend directory and run tests
    # Vitest config expects to run from frontend directory
    cd frontend
    if ../node_modules/.bin/vitest run; then
        echo -e "${GREEN}✅ Frontend tests passed!${NC}"
        FRONTEND_PASSED=1
        cd "$PROJECT_ROOT"
        return 0
    else
        echo -e "${RED}❌ Frontend tests failed!${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# Run tests
echo -e "${BLUE}════════════════════════════════════════${NC}"
run_backend_tests
BACKEND_EXIT=$?

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
run_frontend_tests
FRONTEND_EXIT=$?

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if [ $BACKEND_PASSED -eq 1 ]; then
    echo -e "Backend:  ${GREEN}✅ PASSED${NC}"
else
    echo -e "Backend:  ${RED}❌ FAILED${NC}"
fi

if [ $FRONTEND_PASSED -eq 1 ]; then
    echo -e "Frontend: ${GREEN}✅ PASSED${NC}"
else
    echo -e "Frontend: ${RED}❌ FAILED${NC}"
fi

echo ""

# Exit with appropriate code
if [ $BACKEND_PASSED -eq 1 ] && [ $FRONTEND_PASSED -eq 1 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
