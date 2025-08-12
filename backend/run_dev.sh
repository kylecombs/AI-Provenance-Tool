#!/bin/bash

# AI Provenance Tool - Development Server Startup Script
# Usage: ./run_dev.sh [port]

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AI Provenance Tool Development Server...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv venv${NC}"
    exit 1
fi

# Check if requirements are installed
if [ ! -f "venv/lib/python3.10/site-packages/fastapi/__init__.py" ]; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Activate virtual environment and start server
echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source venv/bin/activate

# Set default port or use provided argument
PORT=${1:-8000}

# Check if port is already in use and find an alternative
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}⚠️  Port ${port} is already in use${NC}"
        # Try ports 8001-8010
        for alt_port in {8001..8010}; do
            if ! lsof -Pi :$alt_port -sTCP:LISTEN -t >/dev/null ; then
                echo -e "${BLUE}🔄 Using alternative port ${alt_port}${NC}"
                echo $alt_port
                return
            fi
        done
        echo -e "${RED}❌ No available ports found between 8000-8010${NC}"
        exit 1
    else
        echo $port
    fi
}

PORT=$(check_port $PORT)

echo -e "${GREEN}✅ Starting server on port ${PORT}...${NC}"
echo -e "${BLUE}📚 API Documentation: http://localhost:${PORT}/docs${NC}"
echo -e "${BLUE}🏥 Health Check: http://localhost:${PORT}/health${NC}"
echo -e "${BLUE}🛑 Press Ctrl+C to stop${NC}"
echo ""

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT