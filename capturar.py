# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

BASE = "https://multi-pozo-app.preview.emergentagent.com"
CHROME = "/usr/bin/google-chrome"
VP = {"width": 390, "height": 844}


def login(page, email, password):
    page.goto(BASE + "/login", wait_until="domcontentloaded")
    page.get_by_placeholder("Escribe tu correo").wait_for(timeout=30000)
    page.wait_for_timeout(1500)
    page.get_by_placeholder("Escribe tu correo").fill(email)
    page.get_by_placeholder("Escribe tu contrasena").fill(password)
    page.get_by_text("Entrar", exact=True).click()
    page.wait_for_timeout(6000)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True,
                                args=["--no-sandbox", "--disable-dev-shm-usage"])

    # 4.1 Login
    ctx = browser.new_context(viewport=VP)
    pg = ctx.new_page()
    pg.goto(BASE + "/login", wait_until="domcontentloaded")
    pg.get_by_placeholder("Escribe tu correo").wait_for(timeout=30000)
    pg.wait_for_timeout(2500)
    pg.screenshot(path="/app/figura_4_1.png")
    print("OK 4.1 login")
    ctx.close()

    # 4.2 Socio - calendario
    ctx = browser.new_context(viewport=VP)
    pg = ctx.new_page()
    login(pg, "alfredo.velez@isidro.com", "pozo2026")
    pg.wait_for_timeout(2000)
    pg.screenshot(path="/app/figura_4_2.png")
    print("OK 4.2 socio calendario ->", pg.url)
    ctx.close()

    # 4.3 Contador - multas
    ctx = browser.new_context(viewport=VP)
    pg = ctx.new_page()
    login(pg, "contador@isidro.com", "pozo2026")
    pg.wait_for_timeout(2000)
    pg.screenshot(path="/app/figura_4_3.png")
    print("OK 4.3 contador multas ->", pg.url)

    # 4.4 Contador - recorrido
    pg.goto(BASE + "/contador/recorrido", wait_until="domcontentloaded")
    pg.wait_for_timeout(5000)
    pg.screenshot(path="/app/figura_4_4.png")
    print("OK 4.4 contador recorrido ->", pg.url)
    ctx.close()

    browser.close()
print("LISTO")
