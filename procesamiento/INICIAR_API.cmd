@echo off
setlocal
call "%~dp0..\INICIAR.cmd" --sin-navegador %*
exit /b %errorlevel%
