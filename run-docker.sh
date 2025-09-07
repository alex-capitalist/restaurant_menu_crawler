#!/bin/bash

# MenuCrawler Docker Runner
# This script makes it easy to run MenuCrawler in Docker with a local AI model

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}  MenuCrawler Docker Runner${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED} Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED} Neither docker-compose nor 'docker compose' is available.${NC}"
    exit 1
fi

# Function to check if a service is running on a port
check_port() {
    local port=$1
    if command -v nc > /dev/null 2>&1; then
        nc -z localhost $port 2>/dev/null
    elif command -v telnet > /dev/null 2>&1; then
        timeout 1 telnet localhost $port > /dev/null 2>&1
    else
        # Fallback: try to make a simple HTTP request
        curl -s --connect-timeout 1 http://localhost:$port > /dev/null 2>&1
    fi
}

# Check for common AI model servers
echo -e "${YELLOW}🔍 Checking for local AI model servers...${NC}"

MODEL_FOUND=false
MODEL_URL=""

if check_port 1234; then
    echo -e "${GREEN} Found service on port 1234 (likely LM Studio)${NC}"
    MODEL_FOUND=true
    MODEL_URL="http://localhost:1234/v1"
elif check_port 11434; then
    echo -e "${GREEN} Found service on port 11434 (likely Ollama)${NC}"
    MODEL_FOUND=true
    MODEL_URL="http://localhost:11434/v1"
elif check_port 8000; then
    echo -e "${GREEN} Found service on port 8000${NC}"
    MODEL_FOUND=true
    MODEL_URL="http://localhost:8000/v1"
else
    echo -e "${YELLOW}⚠️  No AI model server detected on common ports (1234, 11434, 8000)${NC}"
    echo -e "${YELLOW}   Make sure your AI model server is running before proceeding.${NC}"
fi

# Ask user for confirmation
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

# Set environment variables
if [ "$MODEL_FOUND" = true ]; then
    export OPENAI_API_BASE="$MODEL_URL"
    echo -e "${GREEN} Using model URL: $MODEL_URL${NC}"
fi

# Build and run
echo -e "${BLUE} Building Docker image...${NC}"
$COMPOSE_CMD build

echo -e "${BLUE} Starting MenuCrawler...${NC}"
$COMPOSE_CMD up

echo -e "${GREEN} Done! Check ./output/output.json for results.${NC}"
