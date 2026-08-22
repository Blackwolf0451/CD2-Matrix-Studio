@echo off
setlocal
chcp 65001 >nul
title Build CD2 Matrix Studio

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found.
    pause
    exit /b 1
)

py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

set PYTHONPATH=%CD%\src
py -3 -m pytest -q
if errorlevel 1 (
    echo Tests failed. Build stopped.
    pause
    exit /b 1
)

py -3 -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name CD2-Matrix-Studio ^
    --icon assets\app.ico ^
    --paths src ^
    --add-data "assets;assets" ^
    --add-data "docs;docs" ^
    --hidden-import hid ^
    main.py

if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Portable EXE:
echo %CD%\dist\CD2-Matrix-Studio.exe
echo.
pause
