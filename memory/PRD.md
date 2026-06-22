# PRD - Turnos de Pozo

## Problema original
App hibrida (movil + web, una sola base de codigo Expo) para gestionar turnos de agua
de TRES pozos comunitarios independientes (San Isidro, Zapata, Cardenas). Debe correr en
Expo Go (telefono), Expo Web (laptop) y compilarse a APK con EAS. Multi-tenant (datos
aislados por pozo) y multi-rol (socio: 9 por pozo, contador: 1 por pozo). Espanol Mexico,
MXN, fechas DD/MM/YYYY. Codigo limpio sin trazas de Emergent/IA.

## Arquitectura
- Backend: FastAPI + Motor (MongoDB) + JWT (python-jose) + bcrypt. server.py unico.
- Frontend: Expo SDK 54 + expo-router + TypeScript + react-native-web.
- Auth JWT con claims rol + pozo_id; aislamiento multi-tenant derivado del usuario.
- Rotacion de turnos: diaria mod 9 desde 2026-02-01 en orden de lista. Festivos por pozo
  + Computus (Pascua calculada: Jueves y Viernes Santo).
- Notificaciones: web Notification API + polling /api/notificaciones/pendientes cada 30s;
  movil expo-notifications listo para APK.

## Personas
- Socio: consulta turnos, reporta emergencias, marca dias sin servicio, ve multas, exporta historial.
- Contador: gestiona multas (crear/editar/pagar/eliminar) del pozo.

## Requisitos core (estaticos)
- Vista publica con selector de pozo y tap-para-llamar (modal copiable en web).
- Login JWT + selector de pozo. Dashboard socio (4 tabs) y contador (2 tabs).
- Modulo multas con estados Pagado/No pagado y modales de detalle.
- Calendario de turnos, estadisticas con graficas, historial PDF, modo oscuro persistente.

## Implementado (2026-06-22)
- Backend completo: auth, pozos publicos, socios, turnos/calendario, historial,
  dias-sin-servicio, emergencias, multas CRUD + pagar, notificaciones, estadisticas.
- Seed automatico: 3 pozos + 27 socios + 3 contadores (pass pozo2026).
- Frontend: landing, login, vista publica, dashboards socio y contador, multas (socio
  read-only accordion + contador CRUD con FAB), calendario, estadisticas (chart-kit),
  historial con dropdown de meses + export PDF (expo-print/window.print), perfil con
  modo oscuro y cambio de contrasena, notificaciones (bell + polling + Notification API).
- PhoneFrame web (480px centrado), responsive < 600px.
- Config: app.json, eas.json, .env.example (front+back), .gitignore, README en espanol,
  iniciar.bat, configurar-firewall.bat. Tests pytest (18 pasan).
- Validado por testing agent: 18/18 backend, flujos web OK, sin issues bloqueantes.

## Backlog / pendientes
- P1: Permitir al contador exportar reporte de multas a PDF.
- P1: Filtros/busqueda en lista de multas del contador.
- P2: Editar la fecha de creacion de una multa existente (hoy solo en alta).
- P2: Vista de emergencias historicas para el socio.
- P2: Push notifications reales en movil (requiere build APK + google-services.json).

## Proximos pasos
- Esperar feedback del usuario y priorizar backlog.
