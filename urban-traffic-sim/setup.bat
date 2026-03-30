@echo off
:: =============================================================================
:: setup.bat — Chișinău Urban Traffic Simulation (Windows)
:: =============================================================================

setlocal enabledelayedexpansion

set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

echo [setup] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [setup] ERROR: Python not found. Install Python 3.9+ and retry.
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo [setup] Using Python %PY_VERSION%

if "%1"=="--rebuild" (
    if exist %VENV_DIR% (
        echo [setup] Removing existing virtual environment...
        rmdir /s /q %VENV_DIR%
    )
)

if not exist %VENV_DIR% (
    echo [setup] Creating virtual environment at .\%VENV_DIR%...
    python -m venv %VENV_DIR%
) else (
    echo [setup] Virtual environment already exists. Use --rebuild to recreate.
)

echo [setup] Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

echo [setup] Upgrading pip...
pip install --quiet --upgrade pip

echo [setup] Installing dependencies...
pip install --quiet -r %REQUIREMENTS%

if "%SUMO_HOME%"=="" (
    echo.
    echo [setup] WARNING: SUMO_HOME is not set.
    echo [setup] Install SUMO from https://sumo.dlr.de/docs/Downloads.php
    echo [setup] Then set: set SUMO_HOME=C:\Program Files (x86^)\Eclipse\Sumo
) else (
    echo [setup] SUMO_HOME: %SUMO_HOME%
)

echo.
echo [setup] Setup complete. To activate in a new terminal:
echo.
echo     %VENV_DIR%\Scripts\activate
echo.
echo [setup] Then run:
echo     python scripts\prepare_map.py
echo     python main.py
echo     pytest tests\
echo.
