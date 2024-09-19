:: Script: `.\NConvert-Batch.Bat`

:: Initialization
@echo off
setlocal enabledelayedexpansion
title NConvert-Batch
color 80
echo Initialization Complete.
timeout /t 1 >nul

:: Globals Block - Do not reduce lines, unless instructed relevantly so.
set "PYTHON_VERSION_NODECIMAL=310"
set "PYTHON_EXE_TO_USE"=""
set "GRADIO_VERSION=gradio--3.35.2"
set "PANDAS_VERSION=pandas--1.5.3"
set "NUMPY_VERSION=numpy--1.23.5"

:: DP0 TO SCRIPT BLOCK, DO NOT, MODIFY or MOVE: START
set "ScriptDirectory=%~dp0"
set "ScriptDirectory=%ScriptDirectory:~0,-1%"
cd /d "%ScriptDirectory%"
echo Dp0'd to Script.
:: DP0 TO SCRIPT BLOCK, DO NOT, MODIFY or MOVE: END

:: CHECK ADMIN BLOCK, DO NOT, MODIFY or MOVE: START
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
:: CHECK ADMIN BLOCK, DO NOT, MODIFY or MOVE: END

:: FIND PYTHON BLOCK, DO NOT, MODIFY or MOVE: START
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
:: FIND PYTHON BLOCK, DO NOT, MODIFY or MOVE: END

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
echo ========================================================================================================================
set /p choice=Selection; Menu Options = 1-2, Exit NConvert-Batch = X: 

if "!choice!"=="1" (
    goto run_nconvert
    echo Selected: Run NConvert-Batch
    timeout /t 1 >nul
) else if "!choice!"=="2" (
    echo Selected: Install Requirements
    timeout /t 1 >nul
    goto run_setup_install
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
echo ========================================================================================================================
echo    Run nConvert-Batch
echo ========================================================================================================================
echo.
echo Running Python Gradio Version...
"%PYTHON_EXE_TO_USE%" .\nconvert_batch.py
pause
goto exit

:: Install requirements and capture errors
:run_setup_install
cls
echo ========================================================================================================================
echo    Run Setup-Install
echo ========================================================================================================================
echo.
echo Installing Requirements...
echo.

echo Upgrading Pip..
"%PYTHON_EXE_TO_USE%" -m pip install --upgrade pip
echo Pip Upgraded.
echo.

echo Installing Requirements with Versions:
echo %GRADIO_VERSION%
echo %PANDAS_VERSION%
echo %NUMPY_VERSION%
echo.

set "errorPackages="  :: Initialize error packages list
for %%p in (%GRADIO_VERSION% %PANDAS_VERSION% %NUMPY_VERSION%) do (
    rem Replace "--" with "=="
    set "package=%%p"
    set "packageName=!package:~0,!package:--=!"
    set "packageVersion=!package:~!package:--=!!"
    set "package=!packageName==!packageVersion!"

    echo Installing !package!...
    "%PYTHON_EXE_TO_USE%" -m pip install !package!
    if errorlevel 1 (
        echo Failed to install !package!. Adding to error list...
        set "errorPackages=!errorPackages! !package!"
    ) else (
        echo !package! installed successfully.
    )
    echo.
)
echo.
echo Verifying Packages...
if not "!errorPackages!"=="" (
    echo Error packages found: !errorPackages!
    echo Attempting to force uninstall and reinstall error packages...
    for %%p in (!errorPackages!) do (
        rem Replace "==" with "--" for uninstallation
        set "uninstall_package=%%p"
        set "uninstall_packageName=!uninstall_package:~0,!uninstall_package:===!"
        set "uninstall_packageVersion=!uninstall_package:~!uninstall_package:===!!"
        set "uninstall_package=!uninstall_packageName--!uninstall_packageVersion!"

        echo Force uninstalling !uninstall_package!...
        "%PYTHON_EXE_TO_USE%" -m pip uninstall -y !uninstall_packageName!

        rem Replace "--" with "==" for reinstallation
        set "reinstall_package=%%p"
        set "reinstall_packageName=!reinstall_package:~0,!reinstall_package:===!"
        set "reinstall_packageVersion=!reinstall_package:~!reinstall_package:===!!"
        set "reinstall_package=!reinstall_packageName==!reinstall_packageVersion!"

        echo Reinstalling !reinstall_package!...
        "%PYTHON_EXE_TO_USE%" -m pip install --force-reinstall !reinstall_package!
        if errorlevel 1 (
            echo Failed again to install !reinstall_package!.
        ) else (
            echo !reinstall_package! reinstalled successfully.
        )
    )
) else (
    echo No errors encountered during installation.
)
echo.
echo Detailing All Python Compatibility Issues...
"%PYTHON_EXE_TO_USE%" -m pip check
if errorlevel 1 (
    echo Warning: Conflicts Exist.
    timeout /t 2 >nul
) else (
    echo Requirements Installed.
)
echo.

Echo Installation complete
echo.
echo Please review the output above.
echo.
pause
goto :main_menu

:end_of_file
cls  :: do not remove line
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