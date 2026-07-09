# Turnos de Pozo

Aplicacion hibrida (movil + web) para gestionar los turnos de tres pozos de agua
comunitarios independientes: **San Isidro**, **Zapata** y **Cardenas**. Una sola base
de codigo corre en el telefono (Android/iOS con Expo Go) y en el navegador de la laptop
(Expo Web), ademas de poder compilarse a APK con EAS Build.

## Caracteristicas

- Multi-pozo (multi-tenant): los datos de cada pozo estan totalmente aislados.
- Multi-rol: **socio** (9 por pozo) y **contador** (1 por pozo).
- Vista publica con selector de pozo, lista de socios y turno actual (refresco cada 60s).
- Dashboard del socio: Inicio (turno de hoy, calendario, emergencias, recorrido, multas),
  Estadisticas con graficas, Historial mensual con exportacion a PDF y Perfil.
- Dashboard del contador: gestion completa de multas (crear, editar, marcar pagada,
  eliminar) y Perfil.
- Multas con etiqueta "Pagado" (verde) o "No pagado" (rojo) y modales de detalle.
- Notificaciones: en web mediante la Notification API del navegador + polling cada 30s;
  en movil quedan listas para Expo Push al compilar el APK.
- Modo oscuro persistente. Espanol (Mexico), montos en MXN y fechas DD/MM/YYYY.
- Layout responsive: en pantallas grandes la app se centra en una columna de 480px
  simulando un telefono; en pantallas pequenas ocupa toda la pantalla.

## Stack tecnico

- **Frontend:** React Native + Expo SDK 54 + TypeScript, Expo Router, react-native-web,
  Axios, react-native-chart-kit, expo-print, expo-clipboard, expo-notifications.
- **Backend:** FastAPI + Motor (MongoDB async) + JWT (python-jose) + bcrypt.
- **Base de datos:** MongoDB.

## Requisitos

- Node.js 20 o superior
- Python 3.11 o superior
- MongoDB en ejecucion (local o remoto)
- Expo CLI (se usa via `npx`, no requiere instalacion global)
- App **Expo Go** en el celular (para probar en el telefono)

## Instalacion paso a paso

1. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   copy .env.example .env         # y edita los valores
   ```

2. **Frontend**
   ```bash
   cd frontend
   yarn install                   # o npm install
   copy .env.example .env         # y edita EXPO_PUBLIC_API_URL
   ```

## Como correr en la LAPTOP (navegador)

```bash
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```
En otra terminal:
```bash
cd frontend
npx expo start --web
```
Abre **http://localhost:8081** en Chrome, Edge o Firefox.

## Como correr en el TELEFONO (Expo Go)

```bash
cd frontend
npx expo start
```
Escanea el QR con la app Expo Go.

### Conectar el telefono al backend (misma WiFi)

El telefono no puede usar `localhost`. Edita `frontend/.env` y pon la IP local de tu
laptop:
```
EXPO_PUBLIC_API_URL=http://192.168.1.50:8001
```
Para conocer tu IP en Windows ejecuta `ipconfig` y busca "Direccion IPv4".

## Compilar APK con EAS Build

```bash
cd frontend
npm install -g eas-cli
eas login
eas build -p android --profile preview
```
El perfil `preview` genera un APK instalable. El archivo `eas.json` ya esta configurado.

## Notificaciones push en el celular (Android)

Las notificaciones push nativas SOLO funcionan en la app compilada (no en Expo Go ni
en web) y requieren:

1. **Firebase**: crea un proyecto en https://console.firebase.google.com, agrega una app
   Android con el paquete `com.turnosdepozo.app`, descarga el archivo
   **`google-services.json`** y colocalo en la carpeta `frontend/`.
2. **Backend desplegado**: el backend debe estar publicado en internet para poder enviar
   las push (la variable `EMERGENT_PUSH_KEY` se asigna automaticamente en el deploy).
3. **Build de produccion**: `eas build -p android --profile production`.

En web, las notificaciones ya funcionan mediante la Notification API del navegador y el
sondeo cada 30s (no requieren nada de lo anterior).

## Configuracion del Firewall de Windows

Para que el telefono alcance el backend en la misma red, abre los puertos 8001 y 8081.
Ejecuta como Administrador:
```
configurar-firewall.bat
```

## Script de inicio rapido (Windows)

Ejecuta `iniciar.bat` y elige:
- [1] Backend + Frontend WEB (laptop)
- [2] Backend + Frontend MOVIL (QR para Expo Go)
- [3] Solo backend

## Credenciales

Contrasena por defecto de los 30 usuarios: **pozo2026**.
- Contadores: `contador@isidro.com`, `contador@zapata.com`, `contador@cardenas.com`
- Socios: ver `memory/test_credentials.md`.

El backend siembra automaticamente los 3 pozos, 27 socios y 3 contadores al iniciar.

## Estructura del proyecto

```
backend/
  server.py            API FastAPI (auth, multas, turnos, notificaciones, estadisticas)
  requirements.txt
  .env.example
  tests/test_api.py    pruebas pytest
frontend/
  app/                 rutas (expo-router): index, login, publico, socio/, contador/
  src/
    api/               cliente axios
    auth/              contexto de autenticacion
    theme/             colores y modo oscuro
    components/        UI reutilizable (calendario, modales, header, etc.)
    notifications/     contexto de notificaciones (polling + Notification API)
    utils/             formato MXN/fechas, almacenamiento
  app.json  eas.json  .env.example
iniciar.bat            menu de inicio (Windows)
configurar-firewall.bat
```

## Pruebas del backend

```bash
cd backend
pytest -q
```

## Solucion de problemas

- **El telefono no conecta al backend:** verifica que `EXPO_PUBLIC_API_URL` use la IP
  local (no `localhost`) y que el firewall permita el puerto 8001.
- **No abre en el navegador:** confirma que el backend este corriendo en el puerto 8001
  y el frontend en 8081.
- **MongoDB:** asegurate de que el servicio este activo y que `MONGO_URL` sea correcto.
- **Notificaciones web:** el navegador pedira permiso; debe estar concedido.

## Licencia

MIT.
