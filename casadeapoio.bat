@echo off

echo ========================================
echo Iniciando ambiente Casa de Apoio
echo ========================================
echo.

echo [1/3] Iniciando Podman Machine...
podman machine start

echo.
echo [2/3] Iniciando PostgreSQL...
podman start postgres

echo.
echo [3/3] Iniciando Django...
podman start django_casaApoio

echo.
echo Abrindo Casa de Apoio no navegador...
start "" "http://localhost:8000/"

echo.
echo ========================================
echo Ambiente iniciado!
echo ========================================
exit