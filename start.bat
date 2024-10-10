@echo off
REM Define the environment name
SET "ENV_NAME=hbs_temp_python_environment"

REM Function to check for Python 3 and pip
CALL :CHECK_PYTHON
IF %ERRORLEVEL% EQU 1 CALL :ACTIVATE_CONDA

REM Function to check if tkinter is available
CALL :CHECK_TKINTER
IF %ERRORLEVEL% NEQ 0 (
    echo tkinter is not available. Please ensure it is installed before running the application.
    EXIT /B 1
)

REM Install requirements
echo Installing required Python packages...
CALL %PIP_CMD% install -r requirements.txt

REM Run the application
echo Running the application...
CALL %PYTHON_CMD% app.py
GOTO :EOF

:CHECK_PYTHON
FOR /F "tokens=2 delims= " %%V IN ('python --version 2^>^&1') DO SET "PY_VERSION=%%V"
IF "%PY_VERSION:~0,1%"=="3" (
    ECHO Using command python for python3
    SET "PYTHON_CMD=python"
    SET "PIP_CMD=python -m pip"
    EXIT /B 0
) ELSE (
    FOR /F "tokens=2 delims= " %%V IN ('python3 --version 2^>^&1') DO SET "PY_VERSION=%%V"
    IF "%PY_VERSION:~0,1%"=="3" (
        ECHO Using command python3 for python3
        SET "PYTHON_CMD=python3"
        SET "PIP_CMD=python3 -m pip"
        EXIT /B 0
    ) ELSE (
        echo Python 3 is not installed. Trying to check if Anaconda is installed next.
        EXIT /B 1
    )
)

:ACTIVATE_CONDA
CALL conda info --base
IF %ERRORLEVEL% EQU 0 (
    echo Activating Anaconda environment...
    CALL conda activate
    CALL conda create --name %ENV_NAME% python=3.8 -y
    CALL conda activate %ENV_NAME%
    SET "PYTHON_CMD=python"
    SET "PIP_CMD=pip"
) ELSE (
    @REM Check for Conda directly in a common installation path if not found in PATH
    IF EXIST "%ProgramData%\Anaconda3\_conda.exe" (
        echo Found Anaconda at C:\ProgramData\Anaconda3. Activating...
        CALL "%ProgramData%\Anaconda3\Scripts\activate.bat"
        CALL conda create --name %ENV_NAME% python=3.8 -y
        CALL conda activate %ENV_NAME%
        SET "PYTHON_CMD=python"
        SET "PIP_CMD=pip"
        EXIT /B 0
    ) ELSE (
        @REM Check for Conda in the user's AppData if not found in ProgramData
        IF EXIST "%USERPROFILE%\AppData\Local\anaconda3\_conda.exe" (
            echo Found Anaconda in user's AppData. Activating...
            CALL "%USERPROFILE%\AppData\Local\anaconda3\Scripts\activate.bat"
            CALL conda create --name %ENV_NAME% python=3.8 -y
            CALL conda activate %ENV_NAME%
            SET "PYTHON_CMD=python"
            SET "PIP_CMD=pip"
            EXIT /B 0
        )

        IF EXIST "%USERPROFILE%\Anaconda3\_conda.exe" (
            echo Found Anaconda in user's profile directory. Activating...
            CALL "%USERPROFILE%\Anaconda3\Scripts\activate.bat"
            CALL conda create --name %ENV_NAME% python=3.8 -y
            CALL conda activate %ENV_NAME%
            SET "PYTHON_CMD=python"
            SET "PIP_CMD=pip"
            EXIT /B 0
        )
    )
)
echo Anaconda is not installed. Please install Python 3 manually.
EXIT /B 1


:CHECK_TKINTER
CALL %PYTHON_CMD% -c "import tkinter" > NUL 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo tkinter is installed.
    EXIT /B 0
)
EXIT /B 1
