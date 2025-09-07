@echo off
REM Docker Runner for Windows
REM This script makes it easy to run TasteMatch in Docker with a local AI model

echo Docker Runner
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo Error: Neither docker-compose nor 'docker compose' is available.
        pause
        exit /b 1
    ) else (
        set COMPOSE_CMD=docker compose
    )
) else (
    set COMPOSE_CMD=docker-compose
)

echo Checking for local AI model servers...

REM Check common ports (simplified check)
echo Warning: Please ensure your AI model server is running on one of these ports:
echo    - Port 1234 (LM Studio)

echo.
set /p continue="Do you want to continue? (y/N): "
if /i not "%continue%"=="y" (
    echo Aborted.
    pause
    exit /b 0
)

echo Building Docker image...
%COMPOSE_CMD% build

echo Starting TasteMatch crawler...
%COMPOSE_CMD% up

echo Done! Check .\output\output.json for results.
pause
