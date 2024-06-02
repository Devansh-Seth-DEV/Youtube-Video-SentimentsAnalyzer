@echo off

set REQ_FILE=dependencies/deps.txt
set INSTALL_PGK=pip install -r %REQ_FILE%
set FFMPEG_BIN=dependencies/ffmpeg/bin

%INSTALL_PGK%
set PATH=%FFMPEG%;%PATH%
pause
cls