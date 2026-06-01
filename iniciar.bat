@echo off
title Puente de Huellas - Asistencia

echo ========================================
echo    PUENTE DE HUELLAS - ASISTENCIA
echo ========================================
echo.
echo Iniciando servidor...
echo.

start /min BridgeHuellas_Background.exe

timeout /t 3 /nobreak > nul

echo ✅ Servidor iniciado!
echo 📍 URL: http://localhost:8080
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul