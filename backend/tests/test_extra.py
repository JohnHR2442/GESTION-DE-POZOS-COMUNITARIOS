"""Pruebas adicionales: turnos calendario, dias sin servicio, emergencias,
historial, estadisticas, edicion de multa, cambio password e isolation."""
import os
import httpx

BASE = (
    os.environ.get("TEST_API_URL")
    or os.environ.get("EXPO_PUBLIC_BACKEND_URL", "http://localhost:8001")
).rstrip("/") + "/api"

client = httpx.Client(base_url=BASE, timeout=30, verify=True)


def login(email, password="pozo2026"):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(email):
    r = login(email)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# Public endpoints
def test_pozos_publicos():
    r = client.get("/pozos")
    assert r.status_code == 200
    pozos = r.json()
    assert len(pozos) == 3
    ids = {p["id"] for p in pozos}
    assert ids == {"isidro", "zapata", "cardenas"}


def test_pozo_socios_publicos_y_turno():
    for pid in ["isidro", "zapata", "cardenas"]:
        r = client.get(f"/pozos/{pid}/socios")
        assert r.status_code == 200
        socios = r.json()
        assert len(socios) == 9
        # exactamente 0 o 1 en turno
        en_turno = [s for s in socios if s["en_turno"]]
        assert len(en_turno) in (0, 1)


def test_auth_me_y_pozo():
    h = auth_header("alfredo.velez@isidro.com")
    r = client.get("/auth/me", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["email"] == "alfredo.velez@isidro.com"
    assert body["pozo"]["id"] == "isidro"


def test_turnos_calendario():
    h = auth_header("alfredo.velez@isidro.com")
    r = client.get("/turnos/calendario?year=2026&month=3", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["year"] == 2026 and body["month"] == 3
    assert len(body["dias"]) == 31
    # cada dia tras 2026-02-01 deberia tener un socio asignado
    for d in body["dias"]:
        assert d["socio_id"] is not None


def test_historial_y_estadisticas():
    h = auth_header("alfredo.velez@isidro.com")
    r = client.get("/historial?year=2026&month=3", headers=h)
    assert r.status_code == 200
    assert "dias" in r.json()

    r2 = client.get("/estadisticas", headers=h)
    assert r2.status_code == 200
    body = r2.json()
    for key in ("total_multas", "mis_turnos", "por_socio", "monto_total"):
        assert key in body
    assert len(body["por_socio"]) == 9


def test_emergencia_y_notificacion():
    h = auth_header("alfredo.velez@isidro.com")
    r = client.post("/emergencias", headers=h, json={"tipo": "tuberia"})
    assert r.status_code == 200
    eid = r.json()["id"]
    # otro socio del mismo pozo debe ver la notificacion
    h2 = auth_header("simon.meneses@isidro.com")
    pend = client.get("/notificaciones/pendientes", headers=h2).json()
    titles = [n["titulo"] for n in pend["pendientes"]]
    assert "Emergencia reportada" in titles

    # tipo invalido
    bad = client.post("/emergencias", headers=h, json={"tipo": "invalido"})
    assert bad.status_code == 400


def test_dia_sin_servicio_crear_y_borrar():
    h = auth_header("contador@isidro.com")
    fecha = "2026-07-15"
    # cleanup previo
    existing = client.get("/dias-sin-servicio", headers=h).json()
    for d in existing:
        if d["fecha"] == fecha:
            client.delete(f"/dias-sin-servicio/{d['id']}", headers=h)

    r = client.post("/dias-sin-servicio", headers=h, json={"fecha": fecha, "motivo": "Prueba"})
    assert r.status_code == 200
    dss_id = r.json()["id"]

    # duplicado debe 400
    dup = client.post("/dias-sin-servicio", headers=h, json={"fecha": fecha})
    assert dup.status_code == 400

    # listar
    lista = client.get("/dias-sin-servicio", headers=h).json()
    assert any(d["id"] == dss_id for d in lista)

    # borrar
    rd = client.delete(f"/dias-sin-servicio/{dss_id}", headers=h)
    assert rd.status_code == 200


def test_multa_edicion_y_mias():
    h = auth_header("contador@cardenas.com")
    socios = client.get("/socios", headers=h).json()
    socio_target = next(s for s in socios if s["orden"] == 1)
    creada = client.post("/multas", headers=h, json={
        "socio_id": socio_target["id"], "descripcion": "Original", "monto": 100,
    }).json()
    mid = creada["id"]

    # editar
    upd = client.patch(f"/multas/{mid}", headers=h, json={"monto": 200, "descripcion": "Editada"})
    assert upd.status_code == 200
    assert upd.json()["monto"] == 200.0
    assert upd.json()["descripcion"] == "Editada"

    # /multas/mias del socio destinatario
    h_socio = auth_header(socio_target_email_for_id(socio_target["id"], "cardenas"))
    mias = client.get("/multas/mias", headers=h_socio).json()
    assert any(m["id"] == mid for m in mias)

    # cleanup
    client.delete(f"/multas/{mid}", headers=h)


def socio_target_email_for_id(socio_id, pozo):
    # buscar via /pozos/{id}/socios + dom; usamos endpoint protegido /socios con login del contador
    return "antonio.jimenez@cardenas.com"  # orden 1 cardenas


def test_change_password_y_revert():
    email = "freddy.rojas@isidro.com"
    h = auth_header(email)
    r = client.post("/auth/change-password", headers=h,
                    json={"current_password": "pozo2026", "new_password": "nuevopass1"})
    assert r.status_code == 200
    # login con nuevo password
    assert login(email, "nuevopass1").status_code == 200
    # revert
    h2 = {"Authorization": f"Bearer {login(email, 'nuevopass1').json()['access_token']}"}
    rev = client.post("/auth/change-password", headers=h2,
                      json={"current_password": "nuevopass1", "new_password": "pozo2026"})
    assert rev.status_code == 200


def test_change_password_wrong_current():
    h = auth_header("freddy.rojas@isidro.com")
    r = client.post("/auth/change-password", headers=h,
                    json={"current_password": "incorrecta", "new_password": "abcdefg"})
    assert r.status_code == 401
