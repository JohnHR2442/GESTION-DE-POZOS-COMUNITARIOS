# Credenciales de prueba - Turnos de Pozo

Contrasena por defecto para los 30 usuarios: **pozo2026**

## Contadores (rol: contador)
- contador@isidro.com / pozo2026
- contador@zapata.com / pozo2026
- contador@cardenas.com / pozo2026

## Pozo San Isidro (rol: socio)
- alfredo.velez@isidro.com / pozo2026
- simon.meneses@isidro.com / pozo2026
- francisco.meneses@isidro.com / pozo2026
- jose.huerta@isidro.com / pozo2026
- marcelino.huerta@isidro.com / pozo2026
- sidoro.meneses@isidro.com / pozo2026
- lilian.ramirez@isidro.com / pozo2026
- freddy.garcia@isidro.com / pozo2026
- freddy.rojas@isidro.com / pozo2026

## Pozo Zapata (rol: socio)
- jorge.velez@zapata.com / pozo2026
- josefa.zavaleta@zapata.com / pozo2026
- ivan.meneses@zapata.com / pozo2026
- isael.gil@zapata.com / pozo2026
- jorge.rojas@zapata.com / pozo2026
- alexander.rojas@zapata.com / pozo2026
- angel.perez@zapata.com / pozo2026
- freddy.garcia@zapata.com / pozo2026
- oscar.meneses@zapata.com / pozo2026

## Pozo Cardenas (rol: socio)
- antonio.jimenez@cardenas.com / pozo2026
- manuel.meneses@cardenas.com / pozo2026
- alan.huerta@cardenas.com / pozo2026
- gabino.huerta@cardenas.com / pozo2026
- david.velez@cardenas.com / pozo2026
- ismael.rojas@cardenas.com / pozo2026
- dario.duran@cardenas.com / pozo2026
- francisco.rojas@cardenas.com / pozo2026
- edwin.jeronimo@cardenas.com / pozo2026

## Notas para testing
- Endpoint login: POST /api/auth/login  body JSON {email, password}
- Respuesta: {access_token, token_type, user, pozo}
- Header autenticado: Authorization: Bearer <access_token>
- Aislamiento multi-tenant por pozo_id; rol socio (9 por pozo) y contador (1 por pozo).
