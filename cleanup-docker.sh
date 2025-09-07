#!/bin/bash

# MenuCrawler Docker Cleanup Script
# This script removes the MenuCrawler Docker container and related resources

echo "MenuCrawler Docker Cleanup"
echo "============================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[Error] Docker is not running. Please start Docker first."
    exit 1
fi

echo "Finding MenuCrawler containers and images..."

# Stop and remove the container if it exists
echo "Stopping and removing container..."
docker stop menucrawler > /dev/null 2>&1
docker rm menucrawler > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[info] Container 'menucrawler' removed"
else
    echo "[Warning] Container 'menucrawler' not found or already removed"
fi

# Remove the image if it exists
echo "Removing Docker image..."
docker rmi menucrawler:latest > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[info] Image 'menucrawler:latest' removed"
else
    echo "[Warning] Image 'menucrawler:latest' not found or already removed"
fi

# Remove any dangling images related to this project
echo "Cleaning up dangling images..."
docker image prune -f > /dev/null 2>&1
echo "[info] Dangling images cleaned up"

# Ask about volumes
echo ""
read -p "Remove unused volumes? (y/N): " cleanup_volumes
if [[ $cleanup_volumes =~ ^[Yy]$ ]]; then
    docker volume prune -f > /dev/null 2>&1
    echo "[info] Unused volumes removed"
else
    echo "[Warning] Skipping volume cleanup"
fi

# Ask about networks
echo ""
read -p "Remove unused networks? (y/N): " cleanup_networks
if [[ $cleanup_networks =~ ^[Yy]$ ]]; then
    docker network prune -f > /dev/null 2>&1
    echo "[info] Unused networks removed"
else
    echo "[Warning] Skipping network cleanup"
fi

echo ""
echo "[info] Cleanup complete!"
echo ""
echo "Remaining Docker resources:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -i menucrawler
if [ $? -ne 0 ]; then
    echo "[Warning] No MenuCrawler images remaining"
fi

echo ""
