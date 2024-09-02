:: SCRIPT: Install-Setup.Bat
@echo off
setlocal EnableDelayedExpansion

:: Persistence Variables
set "PYTHON_VERSION_NODECIMAL=310"
set "PIP_EXE_TO_USE="
set "PYTHON_EXE_TO_USE="

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

cls
echo ========================================================================================================================
echo                                                      Setup-Installer
echo ========================================================================================================================
echo.
echo Admin Status: Administrator 
echo Working Folder: %Script_Directory%
timeout /t 1 >nul

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

:: Ensure setuptools and wheel are correctly installed
echo Ensuring setuptools and wheel are properly installed...
"%PIP_EXE_TO_USE%" install --upgrade --force-reinstall setuptools wheel
if errorlevel 1 (
    echo Failed to reinstall setuptools and wheel. Carrying On...
)
echo Setuptools and Wheel, Processes Finished.
echo.

:: Install requirements and verify Install.
echo Installing Requirements...
"%PIP_EXE_TO_USE%" install -r requirements.txt
echo Processed: `requirements.txt`
echo.
echo Verifying installation...
"%PIP_EXE_TO_USE%" check
if errorlevel 1 (
    echo Warning: Some conflicts may still exist. Please review the output above.
) else (
    echo All packages are installed correctly with no conflicts.
)
echo.

:end_of_file
echo ========================================================================================================================
echo All processes finished.
pause
exit /b