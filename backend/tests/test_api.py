"""Pruebas de integracion del backend de Turnos de Pozo.

Cubren: autenticacion, roles, aislamiento multi-tenant, multas (fechas de
creacion y pago) y notificaciones.

El backend debe estar en ejecucion antes de correr las pruebas:
    python -m uvicorn server:app --port 8001
Luego:
    pytest -q
"""
import os
import httpx

BASE = os.environ.get("TEST_API_URL", os.environ.get("EXPO_PUBLIC_BACKEND_URL", "http://localhost:8001")).rstrip("/") + "/api"
client = httpx.Client(base_url=BASE, timeout=20)


def login(email, password="pozo2026"):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(email):
    token = login(email).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --------------------------- Autenticacion ---------------------------
def test_login_correcto():
    r = login("contador@isidro.com")
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["rol"] == "contador"
    assert body["user"]["pozo_id"] == "isidro"


def test_login_incorrecto():
    assert login("contador@isidro.com", "malpassword").status_code == 401


def test_me_requiere_token():
    assert client.get("/auth/me").status_code == 401


# --------------------------- Roles ---------------------------
def test_socio_no_puede_crear_multa():
    headers = auth_header("alfredo.velez@isidro.com")
    socios = client.get("/socios", headers=headers).json()
    r = client.post("/multas", headers=headers, json={
        "socio_id": socios[0]["id"], "descripcion": "Prueba", "monto": 100,
    })
    assert r.status_code == 403


# --------------------------- Multas + fechas ---------------------------
def test_crear_pagar_multa_conserva_fechas():
    headers = auth_header("contador@isidro.com")
    socios = client.get("/socios", headers=headers).json()
    creada = client.post("/multas", headers=headers, json={
        "socio_id": socios[0]["id"], "descripcion": "Multa de prueba", "monto": 250.5,
        "fecha_creacion": "2026-03-10",
    }).json()
    assert creada["estado"] == "no_pagado"
    assert creada["fecha_creacion"] == "2026-03-10"
    assert creada["fecha_pago"] is None

    pagada = client.post(f"/multas/{creada['id']}/pagar", headers=headers).json()
    assert pagada["estado"] == "pagado"
    assert pagada["fecha_creacion"] == "2026-03-10"  # se conserva
    assert pagada["fecha_pago"] is not None  # se asigna al pagar

    client.delete(f"/multas/{creada['id']}", headers=headers)


# --------------------------- Multi-tenant ---------------------------
def test_aislamiento_multitenant():
    h_isidro = auth_header("contador@isidro.com")
    socios = client.get("/socios", headers=h_isidro).json()
    creada = client.post("/multas", headers=h_isidro, json={
        "socio_id": socios[0]["id"], "descripcion": "Solo isidro", "monto": 99,
    }).json()

    h_zapata = auth_header("contador@zapata.com")
    multas_zapata = client.get("/multas", headers=h_zapata).json()
    assert creada["id"] not in [m["id"] for m in multas_zapata]

    client.delete(f"/multas/{creada['id']}", headers=h_isidro)


# --------------------------- Notificaciones ---------------------------
def test_notificacion_pendientes():
    headers = auth_header("contador@cardenas.com")
    socios = client.get("/socios", headers=headers).json()
    creada = client.post("/multas", headers=headers, json={
        "socio_id": socios[0]["id"], "descripcion": "Genera notificacion", "monto": 50,
    }).json()

    h_socio = auth_header("antonio.jimenez@cardenas.com")
    pend = client.get("/notificaciones/pendientes", headers=h_socio).json()
    assert "pendientes" in pend
    assert "server_time" in pend

    client.delete(f"/multas/{creada['id']}", headers=headers)


# --------------------------- Vista publica ---------------------------
def test_vista_publica_socios():
    r = client.get("/pozos/isidro/socios")
    assert r.status_code == 200
    socios = r.json()
    assert len(socios) == 9
    assert "en_turno" in socios[0]
