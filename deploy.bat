@echo off
cd /d C:\_Tmp\INTEGRACIONES\ABONOS_APP

echo ============================
echo Subiendo cambios a GitHub...
echo ============================

git add .

git commit -m "update automatico"

git push

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ? Error en push, intentando configurar upstream...
    git push --set-upstream origin main
)

echo.
echo ============================
echo Listo! Si no hubo errores, Render se actualiza solo
echo ============================

pause