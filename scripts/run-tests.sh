#!/bin/bash

# CV Generator - Run All Tests and Linting
# This script runs linting, formatting checks, and tests for backend and frontend
#
# Usage:
#   ./scripts/run-tests.sh                    # Run all (lint + tests, excludes integration tests)
#   ./scripts/run-tests.sh --integration      # Run ONLY integration tests
#   ./scripts/run-tests.sh --lint-only        # Run ONLY linting (no tests)
#   ./scripts/run-tests.sh --test-only        # Run ONLY tests (no linting)
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
LINT_ONLY=0
TEST_ONLY=0

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
        --lint-only|-l)
            LINT_ONLY=1
            shift
            ;;
        --test-only|-t)
            TEST_ONLY=1
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
    echo "CV Generator Test & Lint Runner"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run-tests.sh                    Run all (lint + tests, excludes integration)"
    echo "  ./scripts/run-tests.sh --integration      Run ONLY integration tests"
    echo "  ./scripts/run-tests.sh --lint-only        Run ONLY linting (no tests)"
    echo "  ./scripts/run-tests.sh --test-only        Run ONLY tests (no linting)"
    echo "  ./scripts/run-tests.sh -l                 Short form for --lint-only"
    echo "  ./scripts/run-tests.sh -t                 Short form for --test-only"
    echo "  ./scripts/run-tests.sh -i                 Short form for --integration"
    echo "  ./scripts/run-tests.sh --help             Show this help message"
    echo ""
    echo "Options:"
    echo "  --integration, -i    Run ONLY integration tests (WARNING: These tests run against"
    echo "                       the live Neo4j database and may delete data!)"
    echo "  --lint-only, -l      Run only linting checks (flake8, eslint, prettier)"
    echo "  --test-only, -t      Run only tests (skip linting)"
    exit 0
fi

echo -e "${BLUE}🧪 Running CV Generator Tests & Linting...${NC}"
echo ""

# Fail-fast mode: script exits immediately on first failure

# Function to run flake8 (backend linting)
run_flake8() {
    echo -e "${BLUE}🐍 Running flake8 (Python linting)...${NC}"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker is not running. Skipping flake8.${NC}"
        return 1
    fi

    # Check if containers are running
    if ! docker-compose ps | grep -q "cv-app.*Up"; then
        echo -e "${YELLOW}⚠️  Backend container is not running. Starting it...${NC}"
        docker-compose up -d app
        sleep 5
    fi

    if docker-compose exec -T app flake8 backend --config=.flake8; then
        echo -e "${GREEN}✅ flake8 passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ flake8 failed!${NC}"
        return 1
    fi
}

# Function to run ESLint (frontend linting)
run_eslint() {
    echo -e "${BLUE}📝 Running ESLint (TypeScript linting)...${NC}"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
        npm install
    fi

    cd frontend
    if ../node_modules/.bin/eslint src --ext .ts,.tsx; then
        echo -e "${GREEN}✅ ESLint passed!${NC}"
        cd "$PROJECT_ROOT"
        return 0
    else
        echo -e "${RED}❌ ESLint failed!${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# Function to run Prettier (frontend formatting check)
run_prettier() {
    echo -e "${BLUE}✨ Running Prettier (formatting check)...${NC}"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
        npm install
    fi

    cd frontend
    if ../node_modules/.bin/prettier --check "src/**/*.{ts,tsx,css}"; then
        echo -e "${GREEN}✅ Prettier passed!${NC}"
        cd "$PROJECT_ROOT"
        return 0
    else
        echo -e "${RED}❌ Prettier failed! Run 'npm run format:frontend' to fix.${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

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
    # When --integration flag is provided, run ONLY integration tests without coverage requirements
    if [ $RUN_INTEGRATION -eq 1 ]; then
        PYTEST_CMD="python -m pytest -c backend/pytest.ini -m integration --no-cov"
    else
        PYTEST_CMD="python -m pytest -c backend/pytest.ini"
    fi

    # Run backend tests
    if docker-compose exec -T app $PYTEST_CMD; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
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
        cd "$PROJECT_ROOT"
        return 0
    else
        echo -e "${RED}❌ Frontend tests failed!${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# Run linting and tests based on flags
# Exit immediately on first failure (fail-fast mode)

# Run linting (unless --test-only or --integration)
if [ $TEST_ONLY -eq 0 ] && [ $RUN_INTEGRATION -eq 0 ]; then
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}🔍 LINTING${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""

    if ! run_flake8; then
        echo -e "${RED}❌ Stopping at first failure (flake8)${NC}"
        exit 1
    fi
    echo ""

    if ! run_eslint; then
        echo -e "${RED}❌ Stopping at first failure (ESLint)${NC}"
        exit 1
    fi
    echo ""

    if ! run_prettier; then
        echo -e "${RED}❌ Stopping at first failure (Prettier)${NC}"
        exit 1
    fi
    echo ""
fi

# Run tests (unless --lint-only)
if [ $LINT_ONLY -eq 0 ]; then
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}🧪 TESTS${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""

    if ! run_frontend_tests; then
        echo -e "${RED}❌ Stopping at first failure (Frontend tests)${NC}"
        exit 1
    fi
    echo ""

    if ! run_backend_tests; then
        echo -e "${RED}❌ Stopping at first failure (Backend tests)${NC}"
        exit 1
    fi
    echo ""
fi

# Summary - if we reach here, everything passed
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# Show linting results (if run)
if [ $TEST_ONLY -eq 0 ] && [ $RUN_INTEGRATION -eq 0 ]; then
    echo -e "${BLUE}Linting:${NC}"
    echo -e "  flake8:   ${GREEN}✅ PASSED${NC}"
    echo -e "  ESLint:   ${GREEN}✅ PASSED${NC}"
    echo -e "  Prettier: ${GREEN}✅ PASSED${NC}"
    echo ""
fi

# Show test results (if run)
if [ $LINT_ONLY -eq 0 ]; then
    echo -e "${BLUE}Tests:${NC}"
    echo -e "  Frontend: ${GREEN}✅ PASSED${NC}"
    echo -e "  Backend:  ${GREEN}✅ PASSED${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All checks passed!${NC}"
exit 0
