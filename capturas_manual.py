import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT = "/app/manual_capturas"
os.makedirs(OUT, exist_ok=True)


async def esperar(page, texto):
    await page.get_by_text(texto, exact=False).first.wait_for(timeout=40000)
    await page.wait_for_timeout(1800)


async def foto(page, nombre):
    await page.screenshot(path=f"{OUT}/{nombre}.png", full_page=False)
    print("captura", nombre)


async def login(page, pozo, email):
    await page.goto(BASE)
    await esperar(page, "Selecciona tu pozo")
    await page.get_by_test_id(f"pozo-card-{pozo}").click()
    await page.get_by_test_id("btn-iniciar-sesion").click()
    await esperar(page, "Correo electronico")
    await page.get_by_test_id("input-email").fill(email)
    await page.get_by_test_id("input-password").fill("pozo2026")
    return page


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        page = await ctx.new_page()

        # Datos ilustrativos de multas (solo visuales, no se guardan en el servidor)
        async def mock_multas(route):
            req = route.request
            if req.method != "GET":
                await route.abort()
                return
            r = await ctx.request.get(req.url.split("/api/")[0] + "/api/socios", headers=req.headers)
            socios = {s["nombre"]: s["id"] for s in await r.json()}
            def sid(n):
                return next((v for k, v in socios.items() if k.startswith(n)), "x")
            data = [
                {"id": "m1", "socio_id": sid("Simon Meneses"), "socio_nombre": "Simon Meneses",
                 "descripcion": "Uso del agua fuera de turno", "monto": 300, "estado": "no_pagado",
                 "fecha_creacion": "2026-10-15", "fecha_pago": None},
                {"id": "m2", "socio_id": sid("Jose Isabel Huerta"), "socio_nombre": "Jose Isabel Huerta",
                 "descripcion": "Inasistencia a faena comunitaria", "monto": 200, "estado": "pagado",
                 "fecha_creacion": "2026-10-10", "fecha_pago": "2026-10-12"},
                {"id": "m3", "socio_id": sid("Freddy Garcia"), "socio_nombre": "Freddy Garcia",
                 "descripcion": "Retraso en pago de cooperacion", "monto": 150, "estado": "pagado",
                 "fecha_creacion": "2026-10-05", "fecha_pago": "2026-10-08"},
            ]
            await route.fulfill(json=data)

        async def mock_estad(route):
            await route.fulfill(json={
                "mis_turnos": 39, "mis_multas": 1, "monto_pendiente": 0, "monto_pagado": 200,
                "multas_pagadas": 2, "multas_no_pagadas": 1, "emergencias": 4, "dias_sin_servicio": 1,
                "total_multas": 3,
                "por_socio": [{"nombre": "Simon Meneses", "multas": 1}, {"nombre": "Jose Huerta", "multas": 1},
                              {"nombre": "Freddy Garcia", "multas": 1}, {"nombre": "Alfredo Velez", "multas": 0}],
            })

        await ctx.route("**/api/multas", mock_multas)
        await ctx.route("**/api/estadisticas", mock_estad)
        # Bloquear cualquier escritura al servidor durante las capturas
        async def solo_lectura(route):
            if route.request.method in ("POST", "PATCH", "DELETE", "PUT") and "/auth/login" not in route.request.url:
                await route.abort()
            else:
                await route.fallback()
        await ctx.route("**/api/**", solo_lectura)

        # Pantalla inicial y vista pública
        await page.goto(BASE)
        await esperar(page, "Selecciona tu pozo")
        await page.get_by_test_id("pozo-card-isidro").click()
        await page.wait_for_timeout(600)
        await foto(page, "01_inicio")
        await page.get_by_test_id("btn-soy-usuario").click()
        await esperar(page, "Socios y turno actual")
        await foto(page, "02_publico")

        # Recuperar contraseña
        await page.goto(BASE + "/recuperar")
        await esperar(page, "Recuperar contrasena")
        await foto(page, "03_recuperar")

        # Socio
        await login(page, "isidro", "jose.huerta@isidro.com")
        await foto(page, "04_login")
        await page.get_by_test_id("btn-login").click()
        await esperar(page, "Turno de hoy")
        await foto(page, "05_socio_inicio")
        await page.get_by_test_id("action-emergencia").click()
        await esperar(page, "Reportar emergencia")
        await foto(page, "06_emergencia")
        await page.keyboard.press("Escape")
        await page.goto(BASE + "/socio/inicio")
        await esperar(page, "Turno de hoy")
        await page.get_by_test_id("action-notificaciones").click()
        await page.wait_for_timeout(2000)
        await foto(page, "07_notificaciones")
        await page.goto(BASE + "/socio/multas")
        await esperar(page, "Multas del pozo")
        await foto(page, "08_socio_multas")
        await page.goto(BASE + "/socio/agua-sobra")
        await esperar(page, "Cuantas horas te sobran")
        await foto(page, "09_agua_sobra")
        await page.goto(BASE + "/socio/estadisticas")
        await esperar(page, "Estado de multas del pozo")
        await page.wait_for_timeout(1500)
        await foto(page, "10_estadisticas")
        await page.goto(BASE + "/socio/historial")
        await esperar(page, "Exportar a PDF")
        await foto(page, "11_historial")
        await page.goto(BASE + "/socio/perfil")
        await esperar(page, "Cambiar contrasena")
        await foto(page, "12_perfil")
        await page.get_by_test_id("btn-logout").click()
        await page.wait_for_timeout(1500)

        # Contador
        await login(page, "isidro", "contador@isidro.com")
        await page.get_by_test_id("btn-login").click()
        await esperar(page, "Simon Meneses")
        await foto(page, "13_contador_multas")
        await page.get_by_text("Simon Meneses").first.click()
        await esperar(page, "Marcar pagada")
        await foto(page, "15_multa_detalle")
        await page.get_by_test_id("fab-nueva-multa").click()
        await esperar(page, "Crear multa")
        await foto(page, "14_nueva_multa")
        await page.goto(BASE + "/contador/recorrido")
        await esperar(page, "Toca un dia")
        await foto(page, "16_recorrido")
        await page.get_by_text("28", exact=True).first.click()
        await page.wait_for_timeout(1000)
        await foto(page, "17_recorrido_modal")
        await b.close()


asyncio.run(main())
