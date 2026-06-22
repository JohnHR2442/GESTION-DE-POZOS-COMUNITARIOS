@echo off
chcp 65001 >nul
title Configurar Firewall - Turnos de Pozo
echo Este script abre los puertos 8001 (backend) y 8081 (Expo Web) en el Firewall de Windows.
echo Debe ejecutarse como ADMINISTRADOR.
echo.
pause

netsh advfirewall firewall add rule name="Turnos de Pozo - Backend 8001" dir=in action=allow protocol=TCP localport=8001
netsh advfirewall firewall add rule name="Turnos de Pozo - Expo Web 8081" dir=in action=allow protocol=TCP localport=8081
netsh advfirewall firewall add rule name="Turnos de Pozo - Expo Metro 19000" dir=in action=allow protocol=TCP localport=19000

echo.
echo Reglas creadas correctamente.
pause
