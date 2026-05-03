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
    echo Intentando primer push...
    git push --set-upstream origin main
)

echo.
echo ============================
echo Listo! Render va a actualizar solo
echo ============================

pause





