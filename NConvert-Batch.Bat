:: Script: `.\NConvert-Batch.Bat`

:: Initialization
@echo off
setlocal enabledelayedexpansion
title NConvert-Batch
color 80
echo Initialization Complete.
timeout /t 1 >nul

:: Detect terminal width using PowerShell
for /f "tokens=*" %%a in ('
    powershell -Command ^
        "Get-Host | Select-Object -ExpandProperty UI | Select-Object -ExpandProperty RawUI | Select-Object -ExpandProperty WindowSize | Select-Object -ExpandProperty Width"
') do set TERMINAL_WIDTH=%%a

:: Define separator length based on terminal width
set SEPARATOR_LENGTH=119
if "%TERMINAL_WIDTH%"=="80" set SEPARATOR_LENGTH=79

:: Define separator strings
call :buildSeparator SEPARATOR_LINE_EQ "="
call :buildSeparator SEPARATOR_LINE_DASH "-"

:: Globals Block
set "PYTHON_VERSION_NODECIMAL=39"
set "PYTHON_EXE_TO_USE="

:: Skip headers and function definitions
goto :main_logic

:: Function to build a separator string of specified length and character
:buildSeparator
set "target_var=%~1"
set "char=%~2"
set "line="
for /l %%i in (1,1,%SEPARATOR_LENGTH%) do set "line=!line!%char%"
set "%target_var%=%line%"
goto :eof

:: Function to print a header
:printHeader
echo !SEPARATOR_LINE_EQ!
echo    %~1
echo !SEPARATOR_LINE_EQ!
goto :eof

:: Function to print a separator for prompts
:printSeparator
echo !SEPARATOR_LINE_DASH!
goto :eof

:: Main Logic
:main_logic
:: DP0 TO SCRIPT BLOCK, DO NOT, MODIFY or MOVE: START
set "ScriptDirectory=%~dp0"
set "ScriptDirectory=%ScriptDirectory:~0,-1%"
cd /d "%ScriptDirectory%"
echo Dp0'd to Script.
:: DP0 TO SCRIPT BLOCK, DO NOT, MODIFY or MOVE: END

:: CHECK ADMIN BLOCK
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Error: Admin Required!
    timeout /t 2 >nul
    echo Right Click, Run As Administrator.
    timeout /t 2 >nul
    goto :end_of_file
)
echo Status: Administrator
timeout /t 1 >nul

:: FIND PYTHON BLOCK
for %%I in (
    "C:\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "C:\Program Files\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "%LocalAppData%\Programs\Python\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
) do (
    if exist "%%~I" (
        set "PYTHON_EXE_TO_USE=%%~I"
        goto :found_python
    )
)
echo Error: Python %PYTHON_VERSION_NODECIMAL% not found. Please install Python %PYTHON_VERSION_NODECIMAL%.
goto :end_of_file

:found_python
echo Python %PYTHON_VERSION_NODECIMAL% found.
echo Using `python.exe` from: %PYTHON_EXE_TO_USE%
echo.

:: Main Code Begin
:main_menu
cls
call :printHeader "NConvert-Batch"
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
call :printSeparator
set /p choice=Selection; Menu Options = 1-2, Exit NConvert-Batch = X: 

if "!choice!"=="1" (
    echo Selected: Run NConvert-Batch
    timeout /t 1 >nul
    goto run_nconvert
) else if "!choice!"=="2" (
    echo Selected: Install Requirements
    timeout /t 1 >nul
    goto run_installer
) else if /i "!choice!"=="X" (
    echo Selected: Exit NConvert-Batch
    timeout /t 1 >nul
    goto :end_of_file
) else (
    echo Invalid option. Please try again.
    pause
    goto :main_menu
)

:run_nconvert
cls
call :printHeader "Run NConvert-Batch"
echo.
echo Running Python Gradio Version...
echo Using Python executable: %PYTHON_EXE_TO_USE%
echo.

:: Debug Output: Python Version
echo Checking Python version...
"%PYTHON_EXE_TO_USE%" --version
echo.

:: Debug Output: Installed Packages
echo Listing installed packages...
"%PYTHON_EXE_TO_USE%" -m pip list
echo.

:: Debug Output: Gradio Package Location
echo Checking for gradio package...
"%PYTHON_EXE_TO_USE%" -m pip show gradio
echo.

:: Run the Python script
echo Launching launcher.py...
"%PYTHON_EXE_TO_USE%" .\launcher.py
pause
goto :end_of_file

:: Run Python installer
:run_installer
cls
call :printHeader "Run Installation"
echo.
echo Launching Python installer...
echo Using Python executable: %PYTHON_EXE_TO_USE%
echo.

:: Check if installer.py exists
if not exist ".\installer.py" (
    echo Error: installer.py not found in script directory!
    echo Please ensure installer.py is present and try again.
    echo.
    pause
    goto :main_menu
)

:: Run the Python installer
echo Running installer.py...
echo.
"%PYTHON_EXE_TO_USE%" .\installer.py
echo.

:: Check installer exit code
if errorlevel 1 (
    echo Installation encountered errors.
    echo Please review the output above.
) else (
    echo Installation completed successfully.
)

echo.
pause
goto :main_menu

:end_of_file
cls
call :printHeader "Exit NConvert-Batch"
echo.
timeout /t 1 >nul
echo Exiting NConvert-Batch
timeout /t 1 >nul
echo All processes finished.
timeout /t 1 >nul
exit /b