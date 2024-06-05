@echo off
call config.cmd

title VENV Builder

if  exist %VENV_PATH%/ (
    echo Found virtual environment [%VENV_NAME%]
) else (
	echo Building virtual environment [%VENV_NAME%] ...
    python -m venv %VENV_PATH%
	if %ERRORLEVEL% GEQ 1 (
		echo Failed to create virtual environment [%VENV_NAME%] !
	) else (
		echo Successfully build virtual environment [%VENV_NAME%] .
	)
)

pause