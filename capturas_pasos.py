import asyncio
import json
import os
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT = "/app/manual_pasos"
os.makedirs(OUT, exist_ok=True)
MES = "2026-10"


async def foto(page, nombre):
    await page.wait_for_timeout(900)
    await page.screenshot(path=f"{OUT}/{nombre}.png")
    print("captura", nombre)


async def ver(page, texto, t=40000):
    await page.get_by_text(texto, exact=False).first.wait_for(timeout=t)
    await page.wait_for_timeout(1200)


async def paso(nombre, coro):
    try:
        await coro
    except Exception as e:
        print("FALLO", nombre, str(e)[:150])


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)

        socios_cache = {}

        async def mock(route):
            req = route.request
            u, m = req.url, req.method
            if "/auth/login" in u:
                await route.fallback(); return
            if "/auth/reset/" in u:
                await route.fulfill(json={"ok": True}); return
            if u.endswith("/api/multas") and m == "GET":
                if not socios_cache:
                    r = await ctx.request.get(u.split("/api/")[0] + "/api/socios", headers=req.headers)
                    socios_cache.update({s["nombre"]: s["id"] for s in await r.json()})
                sid = lambda n: next((v for k, v in socios_cache.items() if k.startswith(n)), "x")
                await route.fulfill(json=[
                    {"id": "m1", "socio_id": sid("Simon Meneses"), "socio_nombre": "Simon Meneses",
                     "descripcion": "Uso del agua fuera de turno", "monto": 300, "estado": "no_pagado",
                     "fecha_creacion": "2026-10-15", "fecha_pago": None},
                    {"id": "m2", "socio_id": sid("Jose Isabel Huerta"), "socio_nombre": "Jose Isabel Huerta",
                     "descripcion": "Inasistencia a faena comunitaria", "monto": 200, "estado": "pagado",
                     "fecha_creacion": "2026-10-10", "fecha_pago": "2026-10-12"},
                    {"id": "m3", "socio_id": sid("Freddy Garcia"), "socio_nombre": "Freddy Garcia",
                     "descripcion": "Retraso en pago de cooperacion", "monto": 150, "estado": "pagado",
                     "fecha_creacion": "2026-10-05", "fecha_pago": "2026-10-08"}]); return
            if "/api/estadisticas" in u:
                await route.fulfill(json={"mis_turnos": 39, "mis_multas": 1, "monto_pendiente": 0, "monto_pagado": 200,
                    "multas_pagadas": 2, "multas_no_pagadas": 1, "emergencias": 4, "dias_sin_servicio": 1, "total_multas": 3,
                    "por_socio": [{"nombre": "Simon Meneses", "multas": 1}, {"nombre": "Jose Huerta", "multas": 1},
                                  {"nombre": "Freddy Garcia", "multas": 1}]}); return
            if "/agua-sobra/mias" in u:
                await route.fulfill(json={"horas_sobra": 3}); return
            if "/dias-sin-servicio" in u and m == "GET":
                await route.fulfill(json=[{"id": "d1", "fecha": f"{MES}-27", "tipo": "turno_caido", "motivo": None}]); return
            if m in ("POST", "PATCH", "PUT", "DELETE"):
                await route.fulfill(json={"ok": True, "id": "nuevo"}); return
            await route.fallback()

        await ctx.route("**/api/**", mock)
        page = await ctx.new_page()

        # ---------- Acceso ----------
        await page.goto(BASE)
        await ver(page, "Selecciona tu pozo")
        await page.get_by_test_id("pozo-card-isidro").click()
        await foto(page, "a1_seleccion")
        await page.get_by_test_id("btn-soy-usuario").click()
        await ver(page, "Socios y turno actual")
        await foto(page, "a3_publico")
        await page.goto(BASE)
        await ver(page, "Selecciona tu pozo")
        await page.get_by_test_id("pozo-card-isidro").click()
        await page.get_by_test_id("btn-iniciar-sesion").click()
        await ver(page, "Correo electrónico")
        await foto(page, "a2_login")
        await page.get_by_test_id("input-email").fill("jose.huerta@isidro.com")
        await foto(page, "b1_correo")
        await page.get_by_test_id("input-password").fill("pozo2026")
        await foto(page, "b2_password")
        await page.get_by_test_id("btn-login").click()
        await ver(page, "Turno de hoy")
        await foto(page, "b3_inicio")

        # ---------- Socio ----------
        await page.get_by_test_id("action-emergencia").click()
        await ver(page, "Reportar emergencia")
        await foto(page, "d2_emergencia")
        await paso("emerg", page.locator("[data-testid^='emergencia-']:not([data-testid='emergencia-modal'])").first.click())
        await foto(page, "d3_emergencia_ok")
        await page.goto(BASE + "/socio/inicio"); await ver(page, "Turno de hoy")
        await page.get_by_test_id("action-notificaciones").click()
        await page.wait_for_timeout(2000)
        await foto(page, "d4_notificaciones")
        await paso("leidas", page.get_by_test_id("notif-mark-all").click())
        await foto(page, "d5_leidas")
        await page.goto(BASE + "/socio/multas"); await ver(page, "Multas del pozo")
        await foto(page, "d6_multas")
        await paso("socio", page.get_by_text("Simon Meneses").first.click())
        await foto(page, "d7_multas_socio")
        await paso("detalle", page.get_by_test_id("multa-m1").click())
        await foto(page, "d8_multa_detalle")
        await page.goto(BASE + "/socio/agua-sobra"); await ver(page, "Cuántas horas te sobran")
        await page.get_by_test_id("combo-agregar").click()
        await foto(page, "d9_horas")
        await paso("hora", page.get_by_test_id("hora-3").click())
        await foto(page, "d10_seguro")
        await paso("seguro", page.get_by_test_id("btn-seguro").click())
        await foto(page, "d11_listo")
        await page.goto(BASE + "/socio/agua-sobra"); await ver(page, "Cuántas horas te sobran")
        await paso("quitar", page.get_by_test_id("combo-quitar").click())
        await foto(page, "d12_quitar")
        await page.goto(BASE + "/socio/estadisticas"); await ver(page, "Estado de multas del pozo")
        await foto(page, "d13_estadisticas")
        await page.goto(BASE + "/socio/historial"); await ver(page, "Exportar a PDF")
        await paso("mes", page.get_by_test_id("month-dropdown").click())
        await foto(page, "d14_meses")
        await paso("opt", page.locator("[data-testid^='month-opt-']").nth(1).click())
        await foto(page, "d15_historial")
        await page.goto(BASE + "/socio/perfil"); await ver(page, "Cambiar contraseña")
        await foto(page, "d16_perfil")
        await paso("dark", page.get_by_test_id("toggle-dark-mode").click())
        await foto(page, "d17_oscuro")
        await paso("dark2", page.get_by_test_id("toggle-dark-mode").click())
        await paso("pw1", page.get_by_test_id("input-current-password").fill("pozo2026"))
        await paso("pw2", page.get_by_test_id("input-new-password").fill("nueva2026"))
        await paso("scroll", page.get_by_test_id("btn-change-password").scroll_into_view_if_needed())
        await foto(page, "d18_cambiar_pass")
        await paso("logout", page.get_by_test_id("btn-logout").click())
        await page.wait_for_timeout(1500)
        await foto(page, "d19_logout")

        # ---------- Recuperar ----------
        await page.goto(BASE + "/recuperar"); await ver(page, "Recuperar contraseña")
        await page.get_by_test_id("reset-email").fill("jose.huerta@isidro.com")
        await foto(page, "c1_correo")
        await page.get_by_test_id("reset-next").click()
        await page.get_by_test_id("reset-code").wait_for()
        await page.get_by_test_id("reset-code").fill("482913")
        await foto(page, "c2_codigo")
        await page.get_by_test_id("reset-verify").click()
        await page.get_by_test_id("reset-pass1").wait_for()
        await page.get_by_test_id("reset-pass1").fill("nueva2026")
        await page.get_by_test_id("reset-pass2").fill("nueva2026")
        await foto(page, "c3_nueva")
        await page.get_by_test_id("reset-save").click()
        await page.get_by_test_id("reset-done").wait_for()
        await foto(page, "c4_listo")

        # ---------- Contador ----------
        await page.goto(BASE)
        await ver(page, "Selecciona tu pozo")
        await page.get_by_test_id("pozo-card-isidro").click()
        await page.get_by_test_id("btn-iniciar-sesion").click()
        await page.get_by_test_id("input-email").fill("contador@isidro.com")
        await page.get_by_test_id("input-password").fill("pozo2026")
        await page.get_by_test_id("btn-login").click()
        await ver(page, "Simon Meneses")
        await foto(page, "e1_multas")
        await page.get_by_test_id("fab-nueva-multa").click()
        await ver(page, "Crear multa")
        await foto(page, "e2_form")
        await paso("sel", page.get_by_test_id("select-socio").click())
        await foto(page, "e3_socios")
        await paso("opt", page.locator("[data-testid^='socio-opt-']").nth(1).click())
        await paso("desc", page.get_by_test_id("input-descripcion").fill("Uso del agua fuera de turno"))
        await foto(page, "e4_descripcion")
        await paso("monto", page.get_by_test_id("input-monto").fill("300"))
        await foto(page, "e5_monto")
        await paso("guardar", page.get_by_test_id("btn-save-multa").click())
        await foto(page, "e6_creada")
        await page.goto(BASE + "/contador/multas"); await ver(page, "Simon Meneses")
        await paso("card", page.get_by_test_id("multa-card-m1").click())
        await foto(page, "e7_detalle")
        await paso("pagar", page.get_by_test_id("pagar-m1").click())
        await foto(page, "e8_pagada")
        await page.goto(BASE + "/contador/multas"); await ver(page, "Simon Meneses")
        await paso("card2", page.get_by_test_id("multa-card-m1").click())
        await paso("editar", page.get_by_test_id("editar-m1").click())
        await foto(page, "e9_editar")
        await page.goto(BASE + "/contador/multas"); await ver(page, "Simon Meneses")
        await paso("card3", page.get_by_test_id("multa-card-m1").click())
        await paso("eliminar", page.get_by_test_id("eliminar-m1").click())
        await foto(page, "e10_eliminar")
        await page.goto(BASE + "/contador/recorrido"); await ver(page, "Toca un día")
        await foto(page, "e11_recorrido")
        await paso("dia", page.get_by_text("29", exact=True).first.click())
        await foto(page, "e12_motivo")
        await paso("tipo", page.get_by_test_id("tipo-emergencia").click())
        await paso("motivo", page.get_by_test_id("motivo-input").fill("Falla en la bomba del pozo"))
        await foto(page, "e13_razon")
        await paso("conf", page.get_by_role("button", name="Confirmar").first.click() if False else page.get_by_text("Confirmar", exact=True).last.click())
        await foto(page, "e14_confirmado")
        await page.goto(BASE + "/contador/recorrido"); await ver(page, "Toca un día")
        await paso("dia27", page.get_by_text("27", exact=True).first.click())
        await foto(page, "e15_quitar")
        await b.close()


asyncio.run(main())
