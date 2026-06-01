@echo off
echo ========================================
echo  CONSTRUYENDO PUENTE DE HUELLAS
echo ========================================
echo.

echo [1/4] Instalando dependencias...
pip install pyinstaller flask flask-cors

echo.
echo [2/4] Construyendo ejecutable...
python build_exe.py

echo.
echo [3/4] Creando instalador...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" instalador.iss

echo.
echo [4/4] Creando ZIP final...
cd dist
powershell Compress-Archive -Path * -DestinationPath ..\PuenteHuellas_COMPLETO.zip
cd ..

echo.
echo ========================================
echo  ✅ COMPLETADO!
echo ========================================
echo.
echo Archivos listos para distribuir:
echo   - PuenteHuellas_COMPLETO.zip
echo   - Instalar_Puente_Huellas.exe
echo.
pause