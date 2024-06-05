@echo off
title Scripts Configuration

set PROJ_DIR=%cd%
set VENV_NAME=ytvsa_envy
set VENV_PATH=%PROJ_DIR%/%VENV_NAME%
set VENV_ACTIVATE_PATH=%VENV_PATH%/Scripts
set REQ_FILE=%PROJ_DIR%/dependencies/deps.txt
set FFMPEG_BIN=%PROJ_DIR%/dependencies/ffmpeg/bin
@REM set PATH=%VENV_ACTIVATE_PATH%;%FFMPEG_BIN%;%PATH%