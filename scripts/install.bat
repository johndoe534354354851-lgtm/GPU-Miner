@echo off
setlocal enabledelayedexpansion
echo ============================================
echo   GPU Miner - Smart Installer
echo ============================================
echo.

REM ==========================================
REM Check 1: Python
REM ==========================================
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.12+ from: www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM ==========================================
REM Check 2: NVIDIA GPU
REM ==========================================
echo [2/5] Checking NVIDIA GPU...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] nvidia-smi not found - NVIDIA GPU may not be available
    echo.
    echo This miner requires an NVIDIA GPU with CUDA support.
    echo Please ensure you have:
    echo   1. An NVIDIA GPU ^(GTX 10-series or newer^)
    echo   2. Latest NVIDIA drivers installed
    echo.
    echo Continue anyway? ^(GPU features will be disabled^)
    choice /C YN /M "Continue"
    if !errorlevel! equ 2 exit /b 1
) else (
    echo [OK] NVIDIA GPU detected
    nvidia-smi --query-gpu=name --format=csv,noheader
)
echo.

REM ==========================================
REM Check 3: CUDA Toolkit
REM ==========================================
echo [3/5] Checking CUDA Toolkit...
set CUDA_FOUND=0
set CUDA_PATH_FOUND=

REM Check common CUDA installation paths
for %%v in (13.0 12.6 12.5 12.4 12.3 12.2 12.1 12.0 11.8 11.7) do (
    if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v%%v\bin\nvcc.exe" (
        set CUDA_FOUND=1
        set CUDA_PATH_FOUND=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v%%v
        echo [OK] CUDA Toolkit v%%v found
        goto cuda_check_done
    )
)

:cuda_check_done
if %CUDA_FOUND% equ 0 (
    echo [WARNING] CUDA Toolkit not found
    echo.
    echo CUDA is required for GPU acceleration. Without it, PyCUDA installation will fail.
    echo.
    echo Download CUDA Toolkit from:
    echo   developer.nvidia.com/cuda-downloads
    echo.
    echo Recommended versions: CUDA 11.8, 12.x, or 13.x
    echo.
    echo After installing CUDA, please run this script again.
    echo.
    choice /C YN /M "Continue without CUDA (installation will likely fail)"
    if !errorlevel! equ 2 exit /b 1
)
echo.

REM ==========================================
REM Check 4: Microsoft C++ Build Tools
REM ==========================================
echo [4/5] Checking Microsoft C++ Build Tools...
set MSVC_FOUND=0

REM Check for cl.exe (MSVC compiler)
where cl.exe >nul 2>&1
if %errorlevel% equ 0 (
    set MSVC_FOUND=1
    echo [OK] MSVC compiler found in PATH
    goto msvc_check_done
)

REM Check common Visual Studio paths
for %%v in (2022 2019 2017) do (
    if exist "C:\Program Files\Microsoft Visual Studio\%%v\Community\VC\Tools\MSVC" (
        set MSVC_FOUND=1
        echo [OK] Visual Studio %%v found
        goto msvc_check_done
    )
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\%%v\Community\VC\Tools\MSVC" (
        set MSVC_FOUND=1
        echo [OK] Visual Studio %%v found
        goto msvc_check_done
    )
)

:msvc_check_done
if %MSVC_FOUND% equ 0 (
    echo [WARNING] Microsoft C++ Build Tools not found
    echo.
    echo These tools are required to compile PyCUDA.
    echo.
    echo Option 1 - Build Tools for Visual Studio ^(Recommended^):
    echo   Download from: visualstudio.microsoft.com/downloads/?q=build+tools#build-tools-for-visual-studio-2026
    echo   - Run the installer
    echo   - Select "Desktop development with C++"
    echo   - Install ^(requires ~7GB disk space^)
    echo.
    echo Option 2 - Full Visual Studio Community:
    echo   Download from: visualstudio.microsoft.com/vs/community/
    echo   - Free for individual developers
    echo   - Select "Desktop development with C++" workload
    echo.
    echo After installing, please run this script again.
    echo.
    choice /C YN /M "Continue without C++ Build Tools (PyCUDA installation will fail)"
    if !errorlevel! equ 2 exit /b 1
)
echo.

REM ==========================================
REM Installation
REM ==========================================
echo [5/5] Installing GPU Miner...
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo This may take several minutes, especially for PyCUDA...
echo.
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Common reasons:
    echo   1. Missing CUDA Toolkit - Install from developer.nvidia.com/cuda-downloads
    echo   2. Missing C++ Build Tools - Install from visualstudio.microsoft.com/downloads/?q=build+tools
    echo   3. Incompatible versions - Ensure CUDA 11.8+ and Python 3.12+
    echo.
    echo Please fix the issues above and run this script again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo To start the miner:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Run: python main.py
echo.
echo Or simply run: venv\Scripts\python main.py
echo.
echo For configuration, edit config.yaml
echo.
pause
