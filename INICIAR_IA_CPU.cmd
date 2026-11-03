@echo off
setlocal
cd /d "%~dp0"
if not exist "procesamiento\.venv-neural\instalacion-completa.json" (
  call INICIAR.cmd --instalar-ia --device cpu %*
) else (
  call INICIAR.cmd --device cpu %*
)
exit /b %errorlevel%
