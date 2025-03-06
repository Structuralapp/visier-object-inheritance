@echo off
setlocal

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
    pip install -r requirements.txt
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
