@echo off
setlocal

REM Change directory to script location
cd /d %~dp0

REM Set environment name
set VENV_NAME=visier-object-trace

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Create virtual environment if not exists
if not exist %VENV_NAME% (
    echo Creating virtual environment: %VENV_NAME%
    python -m venv %VENV_NAME%
    REM Install dependencies
    call %VENV_NAME%\Scripts\activate

    REM Upgrade pip and install requirements
    python -m pip install --upgrade pip
    REM Echo current Python version and env
    echo [INFO] Using Python from:
    where python

    REM Upgrade build tools
    python -m pip install --upgrade pip setuptools wheel

    REM Install dependencies using PEP517 build backend
    pip install --use-pep517 -r requirements.txt || (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )

    REM Install Playwright Chrome browser
    echo [INFO] Installing Playwright Chrome browser...
    set PLAYWRIGHT_BROWSERS_PATH=0
    playwright install || (
        echo [ERROR] Failed to install Chrome via Playwright.
        pause
        exit /b 1
    )
    REM Deactivate virtual environment after installation
    REM deactivate
    REM Run Python script
    python visier_object_inheritance_tracing.py
    pause
    exit /b
)

REM Activate virtual environment
call %VENV_NAME%\Scripts\activate

REM Run Python script
python visier_object_inheritance_tracing.py

REM Deactivate virtual environment
REM deactivate

pause
