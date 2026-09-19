"""Backend tests for the new Expo push endpoints and regression checks that
verify creacion de recursos aun funciona cuando crear_notificacion intenta
enviar push a tokens invalidos.

Endpoints cubiertos:
- POST /api/push/register
- GET  /api/push/estado
- POST /api/push/seguir
- POST /api/push/dejar
- POST /api/emergencias
- POST /api/multas
- POST /api/agua-sobra/agregar
- POST /api/dias-sin-servicio
- GET  /api/notificaciones
"""
import os
import uuid
import httpx
import pytest

BASE = (
    os.environ.get("TEST_API_URL")
    or os.environ.get("EXPO_PUBLIC_BACKEND_URL", "http://localhost:8001")
).rstrip("/") + "/api"

client = httpx.Client(base_url=BASE, timeout=30, verify=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def login(email, password="pozo2026"):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(email):
    r = login(email)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def install_id():
    # Un installation_id unico por corrida para no chocar con datos previos.
    return f"TEST_inst_{uuid.uuid4().hex[:12]}"


@pytest.fixture(scope="module")
def expo_token():
    return f"ExponentPushToken[TEST_{uuid.uuid4().hex[:10]}]"


# ---------------------------------------------------------------------------
# Login regression (dos usuarios pedidos)
# ---------------------------------------------------------------------------
def test_login_contador_isidro():
    r = login("contador@isidro.com")
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body and body["access_token"]
    assert body["user"]["rol"] == "contador"
    assert body["user"]["pozo_id"] == "isidro"


def test_login_socio_alfredo():
    r = login("alfredo.velez@isidro.com")
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body and body["access_token"]
    assert body["user"]["rol"] == "socio"
    assert body["user"]["pozo_id"] == "isidro"


# ---------------------------------------------------------------------------
# Push endpoints (no requieren autenticacion)
# ---------------------------------------------------------------------------
def test_push_register_ok(install_id, expo_token):
    r = client.post("/push/register", json={
        "expo_token": expo_token,
        "installation_id": install_id,
        "pozo_ids": ["isidro", "zapata"],
        "user_id": None,
    })
    assert r.status_code == 200, r.text
    assert r.json() == {"ok": True}


def test_push_estado_tras_register(install_id, expo_token):
    r = client.get("/push/estado", params={"installation_id": install_id})
    assert r.status_code == 200
    pozos = r.json()["pozo_ids"]
    assert set(pozos) == {"isidro", "zapata"}, pozos


def test_push_dejar_zapata(install_id, expo_token):
    r = client.post("/push/dejar", json={
        "installation_id": install_id,
        "pozo_id": "zapata",
    })
    assert r.status_code == 200
    # Verificar via /push/estado
    est = client.get("/push/estado", params={"installation_id": install_id}).json()
    assert est["pozo_ids"] == ["isidro"], est


def test_push_seguir_cardenas(install_id):
    r = client.post("/push/seguir", json={
        "installation_id": install_id,
        "pozo_id": "cardenas",
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True
    est = client.get("/push/estado", params={"installation_id": install_id}).json()
    assert "cardenas" in est["pozo_ids"]
    assert "isidro" in est["pozo_ids"]


def test_push_seguir_pozo_inexistente(install_id):
    r = client.post("/push/seguir", json={
        "installation_id": install_id,
        "pozo_id": "pozo-que-no-existe",
    })
    assert r.status_code == 404


def test_push_estado_installation_desconocido():
    r = client.get("/push/estado", params={"installation_id": "no-existe-xyz"})
    assert r.status_code == 200
    assert r.json() == {"pozo_ids": []}


# ---------------------------------------------------------------------------
# Regresion: recursos siguen creandose aunque crear_notificacion envie push
# ---------------------------------------------------------------------------
def test_emergencia_no_falla_por_push(install_id, expo_token):
    # Registrar un dispositivo del pozo isidro para forzar el envio de push
    # con un token invalido -> Expo respondera con error pero enviar_push
    # debe swallowear la excepcion y NO romper la creacion de la emergencia.
    reg = client.post("/push/register", json={
        "expo_token": expo_token,
        "installation_id": install_id,
        "pozo_ids": ["isidro"],
        "user_id": None,
    })
    assert reg.status_code == 200

    h = auth_header("alfredo.velez@isidro.com")
    r = client.post("/emergencias", headers=h, json={"tipo": "tuberia"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("tipo") == "tuberia"
    assert "id" in body


def test_contador_crea_multa_con_push_invalido():
    h = auth_header("contador@isidro.com")
    socios = client.get("/socios", headers=h).json()
    assert len(socios) == 9
    r = client.post("/multas", headers=h, json={
        "socio_id": socios[0]["id"],
        "descripcion": "TEST_push_tolerancia",
        "monto": 111,
    })
    assert r.status_code == 200, r.text
    mid = r.json()["id"]
    # cleanup
    client.delete(f"/multas/{mid}", headers=h)


def test_agua_sobra_agregar_devuelve_horas():
    h = auth_header("alfredo.velez@isidro.com")
    # estado previo
    prev = client.get("/agua-sobra/mias", headers=h).json()["horas_sobra"]
    r = client.post("/agua-sobra/agregar", headers=h, json={"horas": 3})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "horas_sobra" in body
    assert body["horas_sobra"] == prev + 3
    # revertir para no dejar residuos
    rq = client.post("/agua-sobra/quitar", headers=h, json={"horas": 3})
    assert rq.status_code == 200


def test_dia_sin_servicio_socio_crea_ok():
    h = auth_header("alfredo.velez@isidro.com")
    fecha = "2026-07-15"
    # cleanup previo (list publico segun implementacion, aqui protegido)
    existing = client.get("/dias-sin-servicio", headers=h).json()
    for d in existing:
        if d["fecha"] == fecha:
            # borrar con contador (permisos de eliminacion)
            hc = auth_header("contador@isidro.com")
            client.delete(f"/dias-sin-servicio/{d['id']}", headers=hc)

    r = client.post("/dias-sin-servicio", headers=h, json={
        "fecha": fecha, "motivo": "prueba",
    })
    assert r.status_code == 200, r.text
    dss = r.json()
    assert dss["fecha"] == fecha
    # cleanup con contador
    hc = auth_header("contador@isidro.com")
    client.delete(f"/dias-sin-servicio/{dss['id']}", headers=hc)


def test_notificaciones_incluye_generadas():
    h = auth_header("alfredo.velez@isidro.com")
    r = client.get("/notificaciones", headers=h)
    assert r.status_code == 200
    lista = r.json()
    assert isinstance(lista, list)
    # Debe tener al menos una notificacion (generamos varias antes)
    assert len(lista) >= 1
    for n in lista[:5]:
        assert "titulo" in n and "mensaje" in n and "tipo" in n
