#!/bin/bash

# CV Generator - Run All Tests
# This script runs backend and frontend tests
#
# Usage:
#   ./scripts/run-tests.sh                    # Run all tests (excludes integration tests)
#   ./scripts/run-tests.sh --integration      # Run ONLY integration tests
#   ./scripts/run-tests.sh --help             # Show help

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
SHOW_HELP=0
RUN_INTEGRATION=0

for arg in "$@"; do
    case $arg in
        --help|-h)
            SHOW_HELP=1
            shift
            ;;
        --integration|-i)
            RUN_INTEGRATION=1
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Use --help to see usage information"
            exit 1
            ;;
    esac
done

# Show help if requested
if [ $SHOW_HELP -eq 1 ]; then
    echo "CV Generator Test Runner"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run-tests.sh                    Run all tests (backend, frontend, excludes integration)"
    echo "  ./scripts/run-tests.sh --integration       Run ONLY integration tests"
    echo "  ./scripts/run-tests.sh -i                  Short form for --integration"
    echo "  ./scripts/run-tests.sh --help              Show this help message"
    echo ""
    echo "Options:"
    echo "  --integration, -i    Run ONLY integration tests (WARNING: These tests run against"
    echo "                       the live Neo4j database and may delete data!)"
    echo ""
    echo "Note: For E2E tests, use: ./scripts/run-e2e-tests.sh"
    exit 0
fi

echo -e "${BLUE}🧪 Running CV Generator Tests...${NC}"
echo ""

# Track test results
BACKEND_PASSED=0
FRONTEND_PASSED=0

# Function to run backend tests
run_backend_tests() {
    if [ $RUN_INTEGRATION -eq 1 ]; then
        echo -e "${BLUE}📦 Running backend integration tests (in Docker)...${NC}"
        echo -e "${YELLOW}⚠️  WARNING: Integration tests run against the live Neo4j database and may delete data!${NC}"
    else
        echo -e "${BLUE}📦 Running backend tests (in Docker)...${NC}"
    fi

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

    # Build pytest command with optional integration marker
    # Default pytest.ini excludes integration tests with -m "not integration"
    # When --integration flag is provided, run ONLY integration tests
    if [ $RUN_INTEGRATION -eq 1 ]; then
        PYTEST_CMD="python -m pytest -m integration"
    else
        PYTEST_CMD="python -m pytest"
    fi

    # Run backend tests
    if docker-compose exec -T app $PYTEST_CMD || docker-compose run --rm app $PYTEST_CMD; then
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
# Temporarily disable set -e to allow capturing exit codes
set +e

echo -e "${BLUE}════════════════════════════════════════${NC}"
run_backend_tests
BACKEND_EXIT=$?

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
run_frontend_tests
FRONTEND_EXIT=$?

# Re-enable set -e for the rest of the script
set -e

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
ALL_PASSED=1
if [ $BACKEND_PASSED -ne 1 ] || [ $FRONTEND_PASSED -ne 1 ]; then
    ALL_PASSED=0
fi

if [ $ALL_PASSED -eq 1 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
