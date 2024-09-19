:: Script: `.\NConvert-Batch.Bat`

:: Initialization
@echo off
setlocal enabledelayedexpansion
title NConvert-Batch
color 80
echo Initialization Complete.
timeout /t 1 >nul

:: Globals
set "PYTHON_VERSION_NODECIMAL=310"
set "PYTHON_EXE_TO_USE="
set "PIP_EXE_TO_USE="

:: DO NOT MOVE OR UPDATE THIS SECTION: START#
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Error: Admin Required!
    timeout /t 2 >nul
    echo Right Click, Run As Administrator.
    timeout /t 2 >nul
    goto :end_of_script
)
echo Status: Administrator
timeout /t 1 >nul
set "ScriptDirectory=%~dp0"
set "ScriptDirectory=%ScriptDirectory:~0,-1%"
cd /d "%ScriptDirectory%"
echo Dp0'd to Script.
timeout /t 1 >nul
:: DO NOT MOVE OR UPDATE THIS SECTION: END

:: FIND PYTHON BLOCK, DO NOT MODIFY: START
for %%I in (
    "C:\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "C:\Program Files\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "%LocalAppData%\Programs\Python\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
) do (
    if exist "%%~I" (
        set "PYTHON_EXE_TO_USE=%%~dpI\python.exe"
        goto :found_python
    )
)
echo Error: Python %PYTHON_VERSION_NODECIMAL% not found. Please install Python %PYTHON_VERSION_NODECIMAL%.
goto :end_of_file
:found_python
echo Python %PYTHON_VERSION_NODECIMAL% found.
echo Using `python.exe` from: %PYTHON_EXE_TO_USE%
echo.
:: FIND PYTHON BLOCK, DO NOT MODIFY: END

:: Main Code Begin
:main_menu
cls
echo ========================================================================================================================
echo     NConvert-Batch
echo ========================================================================================================================
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo     1. Run NConvert-Batch
echo.
echo     2. Install Requirements
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo ========================================================================================================================
set /p choice=Selection; Menu Options = 1-2, Exit NConvert-Batch = X: 

if "!choice!"=="1" (
    goto run_nconvert
    Selected: Run NConvert-Batch
    timeout /t 1 >nul
) else if "!choice!"=="2" (
    Selected: Run NConvert-Batch
    timeout /t 1 >nul
    goto run_setup_install
) else if /i "!choice!"=="X" (
    Selected: Exit NConvert-Batch
    timeout /t 1 >nul
    goto :end_of_file
) else (
    echo Invalid option. Please try again.
    pause
    goto :main_menu
)

:run_nconvert
cls
echo ========================================================================================================================
echo    Run nConvert-Batch
echo ========================================================================================================================
echo.
echo Running Python Gradio Version...
"%PYTHON_EXE_TO_USE%" .\nconvert_batch.py
pause
goto exit

:run_setup_install
cls
echo ========================================================================================================================
echo    Run Setup-Install
echo ========================================================================================================================
echo.
:: Ensure setuptools and wheel are correctly installed
echo Installing Setuptools and Wheel...
"%PYTHON_EXE_TO_USE%" -m pip install --upgrade setuptools wheel
if errorlevel 1 (
    echo Failed Install: SetupTools and Wheel.
    timeout /t 2 >nul
    echo Carrying On...
    timeout /t 1 >nul
) else (
    echo Setuptools and Wheel installed or already up to date.
)
echo.
echo Installing Requirements...
"%PYTHON_EXE_TO_USE%" -m pip install -r .\requirements.txt
echo Processed: `requirements.txt`
timeout /t 1 >nul
echo Verifying installation...
"%PYTHON_EXE_TO_USE%" -m pip check
if errorlevel 1 (
    echo Warning: Conflicts Exist.
    timeout /t 2 >nul
) else (
    echo Requirements Installed.
)
echo.
echo Please review the output above.
echo.
pause
goto :main_menu

:end_of_file
rem cls  :: do not remove line
echo ========================================================================================================================
echo    Exit NConvert-Batch
echo ========================================================================================================================
echo.
timeout /t 1 >nul
echo Exiting NConvert-Batch
timeout /t 1 >nul
echo All processes finished.
timeout /t 1 >nul
exit /b