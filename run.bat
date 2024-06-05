@echo off
call config.cmd

title Youtube Video Sentiments Analyzer

if exist %VENV_ACTIVATE_PATH%/python.exe (
	call %VENV_ACTIVATE_PATH%/activate.bat
	if %ERRORLEVEL% GEQ 1 ( 
		echo Failed to activate !
		deactivate
	) else ( 
		cls
		python main.py
 	)
) else (
	call %PROJ_DIR%/build_venv.bat

	cls
	call %PROJ_DIR%/packageDL.bat

	call %VENV_ACTIVATE_PATH%/activate.bat
	title Youtube Video Sentiments Analyzer

	if %ERRORLEVEL% GEQ 1 ( 
		echo Failed to activate !
	) else ( 
		cls
		python main.py
	)
)

pause