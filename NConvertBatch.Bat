@echo off
setlocal enabledelayedexpansion
title N Convert Batch
cd /d "%~dp0"
color 80
mode con: cols=49 lines=17

:: Global Variables
set "PYTHON_VERSION_NODECIMAL=310"
set "PYTHON_EXE_TO_USE="
set "PIP_EXE_TO_USE="

:: ADMIN AND DP0, BLOCK, DO NOT MODIFY: START
net session >nul 2>&1 || (
    echo Error: Admin privileges required. Right-click and select "Run as administrator".
    timeout /t 3 >nul
    exit /b 1
)
set "Script_Directory=%~dp0"
set "Script_Directory=%Script_Directory:~0,-1%"
pushd "%Script_Directory%"
:: ...ADMIN AND DP0, BLOCK, DO NOT MODIFY: END

:: FIND PYTHON BLOCK, DO NOT MODIFY: START
for %%I in (
    "C:\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "C:\Program Files\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
    "%LocalAppData%\Programs\Python\Python%PYTHON_VERSION_NODECIMAL%\python.exe"
) do (
    if exist "%%~I" (
        set "PYTHON_EXE_TO_USE=%%~dpI\python.exe"
        set "PIP_EXE_TO_USE=%%~dpI\Scripts\pip.exe"
        goto :found_python
    )
)
echo Error: Python %PYTHON_VERSION_NODECIMAL% not found. Please install Python %PYTHON_VERSION_NODECIMAL%.
goto :end_of_file
:found_python
echo Python %PYTHON_VERSION_NODECIMAL% found.
echo Using `python.exe` from: %PYTHON_EXE_TO_USE%
echo Using `pip.exe` from: %PIP_EXE_TO_USE%
echo.
:: FIND PYTHON BLOCK, DO NOT MODIFY: END

:: Main Code Begin
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
cls
echo.
echo ================(N Convert Batch)================
echo.
echo Running Python Gradio Version...
"%PYTHON_EXE_TO_USE%" .\main_python.py
pause
goto exit

:run_powershell
cls
echo.
echo ================(N Convert Batch)================
echo.
echo Running Powershell Version...
powershell -File .\main_powershell.ps1
pause
goto exit

:exit
echo Exiting...
endlocal
exit
