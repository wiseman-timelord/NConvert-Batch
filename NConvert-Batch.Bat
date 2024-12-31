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
set "PYTHON_EXE_TO_USE="

:: Skip past headers and function definitions
goto :main_logic

:: Function to print a header
:printHeader
echo ========================================================================================================================
echo    %~1
echo ========================================================================================================================
goto :eof

:: Function to print a separator
:printSeparator
echo ========================================================================================================================
goto :eof

:: Main Logic
:main_logic
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
call :printHeader "NConvert-Batch"
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
call :printSeparator
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
call :printHeader "Run nConvert-Batch"
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
echo Launching nconvert_batch.py...
"%PYTHON_EXE_TO_USE%" .\nconvert_batch.py
pause
goto exit

:: Install requirements and capture errors
:run_setup_install
cls
call :printHeader "Run Setup-Install"
echo.
echo Installing Requirements...
echo.

:: Step 1: Check for nconvert.exe and download if missing
if not exist ".\nconvert.exe" (
    echo nconvert.exe not found in the script directory.
    set /p architecture=Select CPU Architecture; x64 = 1, x32 = 2: 
    if "!architecture!"=="1" (
        set "nconvert_url=https://download.xnview.com/NConvert-win64.zip"
        set "nconvert_zip=NConvert-win64.zip"
    ) else if "!architecture!"=="2" (
        set "nconvert_url=https://download.xnview.com/NConvert-win.zip"
        set "nconvert_zip=NConvert-win.zip"
    ) else (
        echo Invalid selection. Exiting.
        pause
        goto :end_of_file
    )

    :: Step 2: Ensure .\data directory exists
    if not exist ".\data" (
        echo Creating .\data directory...
        mkdir ".\data"
        echo .\data directory created.
        echo.
    )

	:: Step 3: Download the ZIP file to .\data
	echo Downloading !nconvert_zip! to .\data...
	powershell -Command "Invoke-WebRequest -Uri '!nconvert_url!' -OutFile '.\data\!nconvert_zip!'"
	if errorlevel 1 (
		echo Failed to download !nconvert_zip!.
		echo Removing incomplete download...
		if exist ".\data\!nconvert_zip!" (
			del ".\data\!nconvert_zip!"
		)
		pause
		goto :end_of_file
	)

    :: Step 4: Unpack the ZIP file into .\data
    echo Unpacking !nconvert_zip!...
    powershell -Command "Expand-Archive -Path '.\data\!nconvert_zip!' -DestinationPath '.\data\' -Force"
    if errorlevel 1 (
        echo Failed to unpack !nconvert_zip!.
        pause
        goto :end_of_file
    )

    :: Step 5: Move contents of .\data\NConvert\ to .\
    if exist ".\data\NConvert\" (
        echo Moving contents of .\data\NConvert\ to .\...
        move ".\data\NConvert\*" ".\"
        echo Moving Plugins folder to .\...
        if exist ".\data\NConvert\Plugins" (
            move ".\data\NConvert\Plugins" ".\"
        )
        echo Deleting empty .\data\NConvert\ folder...
        rmdir /s /q ".\data\NConvert\"
        echo Contents moved and folder deleted.
    )

    :: Step 6: Clean up the ZIP file
    echo Cleaning up...
    del ".\data\!nconvert_zip!"
    echo nconvert.exe successfully downloaded and unpacked.
    echo.
) else (
    echo nconvert.exe already exists in the script directory.
    echo.
)

:: Step 7: Check for .\data directory and create it if it doesn't exist
if not exist ".\data" (
    echo Creating .\data directory...
    mkdir ".\data"
    echo .\data directory created.
    echo.
)

:: Step 8: Create .\data\requirements.txt with the required packages
echo Creating .\data\requirements.txt...
(
    echo gradio==3.35.2
    echo pandas==1.5.3
    echo numpy==1.23.5
    echo psutil==5.9.5
) > ".\data\requirements.txt"
echo .\data\requirements.txt created.
echo.

:: Step 9: Install requirements from .\data\requirements.txt
echo Installing requirements from .\data\requirements.txt...
"%PYTHON_EXE_TO_USE%" -m pip install -r ".\data\requirements.txt"
if errorlevel 1 (
    echo Failed to install requirements.
) else (
    echo Requirements installed successfully.
)
echo.

:: Verify Installation
echo Verifying installed packages...
"%PYTHON_EXE_TO_USE%" -m pip list
echo.

Echo Installation complete
echo.
echo Please review the output above.
echo.
pause
goto :main_menu

:end_of_file
cls  :: do not remove line
call :printHeader "Exit NConvert-Batch"
echo.
timeout /t 1 >nul
echo Exiting NConvert-Batch
timeout /t 1 >nul
echo All processes finished.
timeout /t 1 >nul
exit /b