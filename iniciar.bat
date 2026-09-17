@echo off
chcp 65001 >nul
title Turnos de Pozo - Inicio
:menu
cls
echo ============================================
echo            TURNOS DE POZO
echo ============================================
echo.
echo   [1] Backend + Frontend WEB (laptop)
echo   [2] Backend + Frontend MOVIL (QR Expo Go)
echo   [3] Solo backend
echo   [4] Salir
echo.
set /p opcion="Selecciona una opcion: "

if "%opcion%"=="1" goto web
if "%opcion%"=="2" goto movil
if "%opcion%"=="3" goto backend
if "%opcion%"=="4" exit
goto menu

:backend
echo Iniciando backend en http://localhost:8001 ...
start "Backend" cmd /k "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
goto fin

:web
echo Iniciando backend ...
start "Backend" cmd /k "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 >nul
echo Iniciando frontend WEB en http://localhost:8081 ...
start "Frontend Web" cmd /k "cd frontend && npx expo start --web"
goto fin

:movil
echo Iniciando backend ...
start "Backend" cmd /k "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 >nul
echo Iniciando frontend MOVIL (escanea el QR con Expo Go) ...
start "Frontend Movil" cmd /k "cd frontend && npx expo start"
goto fin

:fin
echo.
echo Servicios iniciados en ventanas separadas.
pause
