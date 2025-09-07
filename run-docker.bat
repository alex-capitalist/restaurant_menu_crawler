@echo off
REM Docker Runner for Windows
REM This script makes it easy to run MenuCrawler in Docker with a local AI model

echo MenuCrawler Docker Runner
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [Error] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [Error] Neither docker-compose nor 'docker compose' is available.
        pause
        exit /b 1
    ) else (
        set COMPOSE_CMD=docker compose
    )
) else (
    set COMPOSE_CMD=docker-compose
)

echo [info] Checking for local AI model servers...

REM Check common ports (simplified check)
echo [Warning]: Please ensure your AI model server is running on one of these ports:
echo    - Port 1234 (LM Studio)

echo.
set /p continue="Do you want to continue? (y/N): "
if /i not "%continue%"=="y" (
    echo [Warning]: Aborted.
    pause
    exit /b 0
)

echo [info] Building Docker image...
echo [info] Use --no-cache flag to force rebuild without cache
%COMPOSE_CMD% build --no-cache

echo [info] Starting MenuCrawler...
%COMPOSE_CMD% up

echo [info] Done! Check .\output\output.json for results.
pause
