#!/bin/bash

# CV Generator - Installation Script
# This script sets up all necessary dependencies and tools for development

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

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}   CV Generator - Installation Script${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
docker_running() {
    docker info >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Check for required tools
echo -e "${BLUE}🔍 Checking for required tools...${NC}"

# Check Docker
if command_exists docker; then
    print_status 0 "Docker is installed"
    if docker_running; then
        print_status 0 "Docker is running"
        DOCKER_AVAILABLE=true
    else
        print_status 1 "Docker is not running"
        echo -e "${YELLOW}⚠️  Please start Docker and run this script again${NC}"
        DOCKER_AVAILABLE=false
    fi
else
    print_status 1 "Docker is not installed"
    echo -e "${YELLOW}⚠️  Please install Docker: https://docs.docker.com/get-docker/${NC}"
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    print_status 0 "Docker Compose is installed"
else
    print_status 1 "Docker Compose is not installed"
    echo -e "${YELLOW}⚠️  Please install Docker Compose${NC}"
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status 0 "Node.js is installed ($NODE_VERSION)"
    NODE_AVAILABLE=true
else
    print_status 1 "Node.js is not installed"
    echo -e "${YELLOW}⚠️  Please install Node.js 18+: https://nodejs.org/${NC}"
    NODE_AVAILABLE=false
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status 0 "npm is installed ($NPM_VERSION)"
else
    print_status 1 "npm is not installed"
    NODE_AVAILABLE=false
fi

# Check Python (optional, only needed if pre-commit isn't available via package manager)
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_status 0 "Python 3 is installed ($PYTHON_VERSION) [optional]"
    PYTHON_AVAILABLE=true
else
    print_status 1 "Python 3 is not installed [optional - only needed for pip install of pre-commit]"
    PYTHON_AVAILABLE=false
fi

echo ""

# Install pre-commit
echo -e "${BLUE}📦 Setting up pre-commit hooks...${NC}"

if command_exists pre-commit; then
    print_status 0 "pre-commit is already installed"
    PRE_COMMIT_AVAILABLE=true
else
    PRE_COMMIT_AVAILABLE=false
    echo -e "${YELLOW}Installing pre-commit...${NC}"

    # Try system package manager first (no Python required)
    if command_exists apt-get && [ "$EUID" -eq 0 ]; then
        # Running as root, try apt
        if apt-get install -y pre-commit >/dev/null 2>&1; then
            print_status 0 "pre-commit installed via apt"
            PRE_COMMIT_AVAILABLE=true
        fi
    elif command_exists apt-get && command_exists sudo; then
        # Try with sudo
        if sudo apt-get install -y pre-commit >/dev/null 2>&1; then
            print_status 0 "pre-commit installed via apt"
            PRE_COMMIT_AVAILABLE=true
        fi
    elif command_exists brew; then
        # Try Homebrew (macOS)
        if brew install pre-commit >/dev/null 2>&1; then
            print_status 0 "pre-commit installed via Homebrew"
            PRE_COMMIT_AVAILABLE=true
        fi
    fi

    # Fallback to pip if package manager didn't work (requires Python)
    if [ "$PRE_COMMIT_AVAILABLE" = false ] && [ "$PYTHON_AVAILABLE" = true ]; then
        echo -e "${BLUE}   Trying pip installation (requires Python)...${NC}"
        # Try pip install with user flag first (safer)
        if python3 -m pip install --user pre-commit 2>/dev/null; then
            print_status 0 "pre-commit installed via pip (user install)"
            # Add user bin to PATH if not already there
            export PATH="$HOME/.local/bin:$PATH"
            PRE_COMMIT_AVAILABLE=true
        elif python3 -m pip install pre-commit 2>/dev/null; then
            print_status 0 "pre-commit installed via pip (system install)"
            PRE_COMMIT_AVAILABLE=true
        fi
    fi

    if [ "$PRE_COMMIT_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⚠️  Could not install pre-commit automatically${NC}"
        echo -e "${YELLOW}   Please install manually using one of:${NC}"
        echo -e "${YELLOW}   - sudo apt install pre-commit${NC}"
        echo -e "${YELLOW}   - brew install pre-commit${NC}"
        if [ "$PYTHON_AVAILABLE" = true ]; then
            echo -e "${YELLOW}   - pip install --user pre-commit${NC}"
        else
            echo -e "${YELLOW}   - pip install --user pre-commit (requires Python 3)${NC}"
        fi
    fi
fi

# Install pre-commit hooks
if command_exists pre-commit; then
    echo -e "${BLUE}Installing git hooks...${NC}"
    if pre-commit install; then
        print_status 0 "Pre-commit hooks installed"
    else
        print_status 1 "Failed to install pre-commit hooks"
    fi
elif [ -f "$HOME/.local/bin/pre-commit" ]; then
    # Try to find pre-commit in common locations
    export PATH="$HOME/.local/bin:$PATH"
    if pre-commit install; then
        print_status 0 "Pre-commit hooks installed"
    else
        print_status 1 "Failed to install pre-commit hooks"
    fi
elif [ "$PRE_COMMIT_AVAILABLE" = false ]; then
    echo -e "${YELLOW}⚠️  pre-commit not found. Please install it and run: pre-commit install${NC}"
fi

echo ""

# Install Node.js dependencies
if [ "$NODE_AVAILABLE" = true ]; then
    echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
    if [ -d "node_modules" ]; then
        echo -e "${YELLOW}node_modules exists, updating dependencies...${NC}"
        npm install
    else
        npm install
    fi
    print_status 0 "Node.js dependencies installed"
else
    echo -e "${YELLOW}⚠️  Skipping Node.js dependencies (Node.js not available)${NC}"
fi

echo ""

# Build Docker images and install Python dependencies
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${BLUE}🐳 Building Docker images and installing Python dependencies...${NC}"
    echo -e "${BLUE}   This may take a few minutes on first run...${NC}"

    # Build the images (this installs Python dependencies)
    if docker-compose build --quiet 2>/dev/null || docker compose build --quiet 2>/dev/null; then
        print_status 0 "Docker images built successfully"
    else
        # Try without quiet flag for better error messages
        if docker-compose build 2>/dev/null || docker compose build 2>/dev/null; then
            print_status 0 "Docker images built successfully"
        else
            print_status 1 "Failed to build Docker images"
            echo -e "${YELLOW}⚠️  You may need to build manually: docker-compose build${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Docker build (Docker not available)${NC}"
fi

echo ""

# Verify installation
echo -e "${BLUE}🔍 Verifying installation...${NC}"

VERIFICATION_FAILED=false

# Check pre-commit hooks
if [ -f ".git/hooks/pre-commit" ]; then
    print_status 0 "Pre-commit hooks are installed"
else
    print_status 1 "Pre-commit hooks are not installed"
    VERIFICATION_FAILED=true
fi

# Check node_modules
if [ -d "node_modules" ] && [ "$(ls -A node_modules 2>/dev/null)" ]; then
    print_status 0 "Node.js dependencies are installed"
else
    print_status 1 "Node.js dependencies are missing"
    VERIFICATION_FAILED=true
fi

# Check Docker images
if [ "$DOCKER_AVAILABLE" = true ]; then
    if docker images | grep -q "cv.*app\|cv.*neo4j" 2>/dev/null || \
       docker images | grep -q "$(basename "$PROJECT_ROOT")" 2>/dev/null; then
        print_status 0 "Docker images are built"
    else
        print_status 1 "Docker images are not built"
        VERIFICATION_FAILED=true
    fi
fi

echo ""

# Final summary
if [ "$VERIFICATION_FAILED" = false ]; then
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}   ✅ Installation Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo -e "Next steps:"
    echo -e "  1. Start development: ${BLUE}./scripts/run-dev.sh${NC}"
    echo -e "  2. Or manually: ${BLUE}docker-compose up -d${NC} then ${BLUE}npm run dev${NC}"
    echo ""
else
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}   ⚠️  Installation completed with warnings${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo ""
    echo -e "Please review the errors above and fix them manually."
    echo ""
fi
