@echo off
setlocal

REM Set Python home manually if needed (update this path)
set PYTHON_HOME=C:\Path\To\Python

REM Set environment name
set VENV_NAME=visier-object-trace

REM Use PYTHON_HOME to call Python
set PYTHON_EXEC=%PYTHON_HOME%\python.exe

REM Check if Python exists at PYTHON_HOME
if not exist %PYTHON_EXEC% (
    echo Python not found at %PYTHON_HOME%. Please check the path.
    exit /b 1
)

REM Create virtual environment if not exists
if not exist %VENV_NAME% (
    echo Creating virtual environment: %VENV_NAME%
    %PYTHON_EXEC% -m venv %VENV_NAME%
    
    REM Activate virtual environment
    call %VENV_NAME%\Scripts\activate
    
    REM Install dependencies
    pip install -r requirements.txt
    
    REM Run Python script
    %PYTHON_EXEC% visier_object_inheritance_tracing.py
    pause
    exit /b
)

REM Activate virtual environment
call %VENV_NAME%\Scripts\activate

REM Run Python script
%PYTHON_EXEC% visier_object_inheritance_tracing.py

REM Deactivate virtual environment
REM deactivate

pause
