@echo off
call config.cmd

title Package Downloader

if exist %VENV_PATH%/ (
	call %VENV_ACTIVATE_PATH%/activate.bat	
	if %ERRORLEVEL% GEQ 1 (
		echo Failed to activate !
	) else ( 
		echo Activated 
		echo Installing packages ...
		pip install -r %REQ_FILE%
		if %ERRORLEVEL% GEQ 1 (
			echo Error occured while downloading packages !
		) else (
			echo Successfully downloaded all packages
		)
		deactivate
	)
) else (
	echo Virtual environment [%VENV_NAME%] not found !
)

pause