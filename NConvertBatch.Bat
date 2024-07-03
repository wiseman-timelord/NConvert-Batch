@echo off
setlocal enabledelayedexpansion
title N Convert Batch
cd /d "%~dp0"
color 80
mode con: cols=49 lines=17

:menu
cls
echo.
echo ================(N Convert Batch)================
echo.
echo.
echo.
echo                   Launcher Menu
echo.
echo            1. Run Python Gradio Version
echo.
echo             2. Run Powershell Version
echo.
echo.
echo.
echo -------------------------------------------------
set /p choice=Selection; Options = 1-2, Exit = X: 

if "!choice!"=="1" (
    goto run_python
) else if "!choice!"=="2" (
    goto run_powershell
) else if /i "!choice!"=="X" (
    goto exit
) else (
    echo Invalid option. Please try again.
    pause
    goto menu
)

:run_python
echo Running Python Gradio Version...
start "" python main_python.py
goto exit

:run_powershell
echo Running Powershell Version...
start "" powershell -File main_powershell.ps1
goto exit

:exit
echo Exiting...
endlocal
exit
