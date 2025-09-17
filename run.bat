@echo off
set VENV_DIR=.vmodules

if "%1"=="venv" (
    echo Creating virtual environment in %VENV_DIR% ...
    python -m venv %VENV_DIR%
    exit /b
)

if "%1"=="activate" (
    echo Activating virtual environment...
    call %VENV_DIR%\Scripts\activate.bat
    exit /b
)

if "%1"=="deactivate" (
    echo To deactivate, run "deactivate" inside the activated shell.
    exit /b
)

if "%1"=="install" (
    echo Installing dependencies from requirements.txt ...
    %VENV_DIR%\Scripts\pip install -r requirements.txt
    exit /b
)

if "%1"=="clean" (
    echo Removing %VENV_DIR% ...
    rmdir /s /q %VENV_DIR%
    exit /b
)


if "%1"=="freeze" (
    echo Documenting the required documents.
    %VENV_DIR%\Scripts\pip freeze > requirements.txt
    exit /b
)

echo.
echo Usage: venv [command]
echo.
echo Commands:
echo   venv       -> create virtual environment
echo   activate   -> activate virtual environment
echo   deactivate -> show how to deactivate
echo   install    -> install dependencies from requirements.txt
echo   clean      -> remove virtual environment
 