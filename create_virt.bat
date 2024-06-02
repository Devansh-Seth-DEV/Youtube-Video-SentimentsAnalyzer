@echo off

set VENY_NAME=asa_envy
set CREAT_VENV=python -m venv %VENY_NAME%
set ACTIVATE_VENV=%VENY_NAME%/Scripts

%CREAT_VENV%
cd %ACTIVATE_VENV% && activate && cd ../..