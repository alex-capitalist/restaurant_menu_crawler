@echo off
REM MenuCrawler Docker Cleanup Script
REM This script removes the MenuCrawler Docker container and related resources

echo MenuCrawler Docker Cleanup
echo ============================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [Error] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo Finding MenuCrawler containers and images...

REM Stop and remove the container if it exists
echo Stopping and removing container...
docker stop menucrawler >nul 2>&1
docker rm menucrawler >nul 2>&1
if errorlevel 1 (
    echo [Warning]: Container 'menucrawler' not found or already removed
) else (
    echo [info] Container 'menucrawler' removed
)

REM Remove the image if it exists
echo Removing Docker image...
docker rmi menucrawler:latest >nul 2>&1
if errorlevel 1 (
    echo [Warning]: Image 'menucrawler:latest' not found or already removed
) else (
    echo [info] Image 'menucrawler:latest' removed
)

REM Force remove all images with menucrawler in the name
echo Removing all MenuCrawler related images...
for /f "tokens=3" %%i in ('docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" ^| findstr /i menucrawler') do (
    docker rmi -f %%i >nul 2>&1
    echo [info] Removed image %%i
)

REM Remove any dangling images related to this project
echo Cleaning up dangling images...
docker image prune -f >nul 2>&1
echo [info] Dangling images cleaned up

REM Remove any unused volumes (optional)
echo.
set /p cleanup_volumes="Remove unused volumes? (y/N): "
if /i "%cleanup_volumes%"=="y" (
    docker volume prune -f >nul 2>&1
    echo [info] Unused volumes removed
) else (
    echo [Warning]: Skipping volume cleanup
)

REM Remove any unused networks (optional)
echo.
set /p cleanup_networks="Remove unused networks? (y/N): "
if /i "%cleanup_networks%"=="y" (
    docker network prune -f >nul 2>&1
    echo [info] Unused networks removed
) else (
    echo [Warning]: Skipping network cleanup
)

echo.
echo [info] Cleanup complete!
echo.
echo Remaining Docker resources:
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | findstr /i menucrawler
if errorlevel 1 (
    echo [Warning]: No MenuCrawler images remaining
)

echo.
pause
