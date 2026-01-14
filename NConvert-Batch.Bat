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
set "PYTHON_EXE_TO_USE="
set "PYTHON_VERSION_FOUND="
set "BEST_SCORE=0"

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

:: FIND PYTHON BLOCK - DYNAMIC DETECTION
echo Searching for Python installations...

rem Define search locations
set "LOC1=%LOCALAPPDATA%\Programs\Python"
set "LOC2=%ProgramFiles%\Python"
set "LOC3=%ProgramFiles(x86)%\Python"

for %%L in ("%LOC1%" "%LOC2%" "%LOC3%") do (
    if exist %%L (
        for /f "delims=" %%D in ('dir /b /s "%%L\python.exe" 2^>nul') do (
            for /f "tokens=2" %%V in ('"%%D" --version 2^>nul') do (
                for /f "tokens=1,2 delims=." %%A in ("%%V") do (
                    set /a "NUM=%%A*100+%%B"
                    if !NUM! geq 308 if !NUM! leq 312 if !NUM! gtr !BEST_SCORE! (
                        set "BEST_SCORE=!NUM!"
                        set "PYTHON_EXE_TO_USE=%%D"
                        set "PYTHON_VERSION_FOUND=%%V"
                    )
                )
            )
        )
    )
)

if not defined PYTHON_EXE_TO_USE (
    echo Error: No Python 3.8-3.12 found. Please install Python from python.org
    timeout /t 3 >nul
    goto :end_of_file
)

echo Python %PYTHON_VERSION_FOUND% found.
echo Using python.exe from: %PYTHON_EXE_TO_USE%
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
echo Launching NConvert Batch Converter...
echo.

:: Run the Python script directly
"%PYTHON_EXE_TO_USE%" .\program.py

:: Check if program exited with error
if errorlevel 1 (
    echo.
    echo Error: Program failed to run properly.
    echo Please run the installer option again from the main menu.
)

pause
goto :main_menu

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