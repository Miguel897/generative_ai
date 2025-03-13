@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Check if a command is provided
IF "%1"=="" (
    echo Usage: make.bat [command]
    exit /b 1
)

SET COMMAND=%1

REM Define a list of commands to execute
IF "%COMMAND%"=="ruff" (
    echo Running Ruff checks...
    ruff check --select I --fix
    ruff format .
    exit /b 0
)