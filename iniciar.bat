@echo off

echo ============================
echo Iniciando servidor Flask...
echo ============================

start "FLASK" cmd /k py C:\_Tmp\INTEGRACIONES\ABONOS_APP\app.py

timeout /t 3 >nul

echo ============================
echo Iniciando ngrok...
echo ============================

start "NGROK" cmd /k C:\_Tmp\INTEGRACIONES\ABONOS_APP\ngrok.exe http 5000

echo ============================
echo Todo iniciado
echo ============================

pause