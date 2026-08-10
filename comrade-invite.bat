@echo off
setlocal
:: Get the directory where this batch file lives
set "PROJECT_ROOT=%~dp0"

:: Execute using the project's virtual environment python
"%PROJECT_ROOT%venv\Scripts\python.exe" "%PROJECT_ROOT%cli\cli_invite.py" %*
endlocal