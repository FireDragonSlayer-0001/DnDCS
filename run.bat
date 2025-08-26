@echo off
setlocal
cd /d "%~dp0"
REM Ensure local src package is on PYTHONPATH so the app can run without installation
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
REM Launch the DnDCS web UI in your browser.
python -m dndcs.cli ui %* || pause
endlocal
