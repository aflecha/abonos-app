@echo off
cd /d C:\_Tmp\INTEGRACIONES\ABONOS_APP

echo ============================
echo Subiendo cambios a GitHub...
echo ============================

git add .
git commit -m "update"
git push

echo ============================
echo Listo! Render se actualiza solo
echo ============================

pause