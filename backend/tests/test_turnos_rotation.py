"""
Tests para la nueva logica de turnos en 'Turnos de Pozo':

1) Calendario isidro Septiembre 2026: festivo 09-15 SIN TURNO, secuencia con
   RECORRIDO. Sept 20 -> Jose Isabel Huerta.
2) Recorrido por dia sin servicio: crear DSS en dia laborable, verificar que
   ese dia queda sin turno y los dias siguientes se recorren. Luego borrarlo.
3) Regla 18:00 cutoff en /pozos/isidro/turno-hoy y consistencia con
   /pozos/isidro/socios (en_turno=True).
4) Regresion: GET /api/pozos (200) y login contador (200).
"""
import os
from datetime import datetime, timezone, timedelta, date

import pytest
import requests

BASE_URL = os.environ.get("BACKEND_TEST_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"

LOCAL_TZ = timezone(timedelta(hours=-6))

# ---------------------------- fixtures ---------------------------------
@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def socio_token(session):
    r = session.post(f"{API}/auth/login", json={
        "email": "jose.huerta@isidro.com",
        "password": "pozo2026",
    })
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def contador_token(session):
    r = session.post(f"{API}/auth/login", json={
        "email": "contador@isidro.com",
        "password": "pozo2026",
    })
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------- regresion --------------------------------
def test_list_pozos_ok(session):
    r = session.get(f"{API}/pozos")
    assert r.status_code == 200, r.text
    pozos = r.json()
    ids = {p["id"] for p in pozos}
    assert {"isidro", "zapata", "cardenas"}.issubset(ids)
    # No debe filtrar _id
    for p in pozos:
        assert "_id" not in p
    isidro = next(p for p in pozos if p["id"] == "isidro")
    assert isidro["inicio"] == "2026-01-05"


def test_login_contador_ok(contador_token):
    assert isinstance(contador_token, str) and len(contador_token) > 10


# ---------------------------- calendario -------------------------------
EXPECTED_SEPT = {
    13: "Lilian Ramirez",
    14: "Freddy Garcia",
    15: None,  # festivo, sin turno
    16: "Freddy Rojas",
    17: "Alfredo Velez",
    18: "Simon Meneses",
    19: "Francisco Meneses",
    20: "Jose Isabel Huerta",
    21: "Marcelino Huerta",
    22: "Sidoro Meneses",
}


def test_calendario_isidro_sept_2026(session, socio_token):
    r = session.get(f"{API}/turnos/calendario",
                    params={"year": 2026, "month": 9},
                    headers=auth(socio_token))
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["year"] == 2026 and payload["month"] == 9
    dias_by_num = {d["dia"]: d for d in payload["dias"]}

    # dia 15: festivo, sin turno
    d15 = dias_by_num[15]
    assert d15["festivo"] is True, d15
    assert d15["socio_nombre"] is None, d15
    assert d15["socio_id"] is None, d15
    assert d15["sin_servicio"] is False, d15

    # dia 20: Jose Isabel Huerta
    d20 = dias_by_num[20]
    assert d20["socio_nombre"] == "Jose Isabel Huerta", d20
    assert d20["festivo"] is False and d20["sin_servicio"] is False

    # secuencia completa (recorrido tras festivo)
    for dia_num, esperado in EXPECTED_SEPT.items():
        got = dias_by_num[dia_num]["socio_nombre"]
        assert got == esperado, f"Sept {dia_num}: esperado={esperado} obtenido={got}"


# ---------------------------- dia sin servicio -------------------------
def test_recorrido_por_dia_sin_servicio(session, socio_token):
    """Marca 2026-10-05 (lunes laborable) como sin servicio y verifica que:
       - ese dia queda sin turno,
       - los siguientes dias se recorren (el socio que tocaba pasa al dia siguiente).
       Al final elimina el DSS.
    """
    fecha_dss = "2026-10-05"

    # Calendario BASE (sin DSS) - obtener socio original de 10-05, 10-06, 10-07
    r0 = session.get(f"{API}/turnos/calendario",
                     params={"year": 2026, "month": 10},
                     headers=auth(socio_token))
    assert r0.status_code == 200, r0.text
    base_by_num = {d["dia"]: d for d in r0.json()["dias"]}
    base_5 = base_by_num[5]["socio_nombre"]
    base_6 = base_by_num[6]["socio_nombre"]
    assert base_5 is not None, "Precondicion: 10-05 debe ser laborable en base"
    assert base_6 is not None, "Precondicion: 10-06 debe ser laborable en base"
    # Verificar que 10-05 no es festivo
    assert base_by_num[5]["festivo"] is False
    assert base_by_num[5]["sin_servicio"] is False

    dss_id = None
    try:
        # Crear DSS
        rc = session.post(f"{API}/dias-sin-servicio",
                          json={"fecha": fecha_dss, "motivo": "TEST_prueba"},
                          headers=auth(socio_token))
        assert rc.status_code == 200, rc.text
        dss = rc.json()
        assert dss["fecha"] == fecha_dss
        assert "_id" not in dss
        dss_id = dss["id"]

        # Calendario con DSS
        r1 = session.get(f"{API}/turnos/calendario",
                         params={"year": 2026, "month": 10},
                         headers=auth(socio_token))
        assert r1.status_code == 200, r1.text
        by_num = {d["dia"]: d for d in r1.json()["dias"]}

        # dia 05: sin servicio, sin turno
        d5 = by_num[5]
        assert d5["sin_servicio"] is True, d5
        assert d5["socio_nombre"] is None, d5
        assert d5["motivo"] == "TEST_prueba", d5

        # RECORRIDO: dia 06 debe traer al socio que originalmente iba el 05
        d6 = by_num[6]
        assert d6["socio_nombre"] == base_5, (
            f"Recorrido incorrecto: 10-06 deberia ser {base_5} (el que tocaba el 05) "
            f"pero es {d6['socio_nombre']}"
        )
        # y el que originalmente iba el 06 ahora va el 07 (si 07 es laborable)
        d7 = by_num[7]
        if d7["sin_servicio"] is False and d7["festivo"] is False:
            assert d7["socio_nombre"] == base_6, (
                f"Recorrido incorrecto: 10-07 deberia ser {base_6} pero es {d7['socio_nombre']}"
            )
    finally:
        # Cleanup: eliminar DSS aunque falle el test
        if dss_id:
            rd = session.delete(f"{API}/dias-sin-servicio/{dss_id}",
                                headers=auth(socio_token))
            assert rd.status_code == 200, rd.text
            # Confirmar que ya no aparece
            r2 = session.get(f"{API}/dias-sin-servicio", headers=auth(socio_token))
            assert r2.status_code == 200
            ids_after = {d["id"] for d in r2.json()}
            assert dss_id not in ids_after


# ---------------------------- 18:00 cutoff -----------------------------
def test_cutoff_18h_turno_hoy(session):
    """La 'fecha' del turno vigente debe ser hoy_local si hora>=18:00,
       y hoy_local - 1 si hora<18:00."""
    r = session.get(f"{API}/pozos/isidro/turno-hoy")
    assert r.status_code == 200, r.text
    data = r.json()
    fecha = date.fromisoformat(data["fecha"])

    now_local = datetime.now(LOCAL_TZ)
    hoy_local = now_local.date()
    if now_local.hour < 18:
        esperado = hoy_local - timedelta(days=1)
    else:
        esperado = hoy_local

    assert fecha == esperado, (
        f"18h cutoff mal: hora_local={now_local.isoformat()}, "
        f"esperada={esperado}, obtenida={fecha}"
    )


def test_turno_hoy_matches_socios_en_turno(session):
    """El socio devuelto por /turno-hoy debe coincidir con el socio marcado
       en_turno=True en /pozos/isidro/socios (o ambos vacios en dia no laborable).
    """
    r1 = session.get(f"{API}/pozos/isidro/turno-hoy")
    assert r1.status_code == 200, r1.text
    t = r1.json()

    r2 = session.get(f"{API}/pozos/isidro/socios")
    assert r2.status_code == 200, r2.text
    socios = r2.json()
    en_turno = [s for s in socios if s.get("en_turno")]

    if t["socio"] is None:
        # dia no laborable
        assert en_turno == [], f"turno-hoy vacio pero hay socios en_turno: {en_turno}"
    else:
        assert len(en_turno) == 1, f"Se esperaba exactamente 1 socio en_turno: {en_turno}"
        assert en_turno[0]["id"] == t["socio"]["id"], (
            f"Discrepancia: turno-hoy={t['socio']}, en_turno={en_turno[0]}"
        )
        assert en_turno[0]["nombre"] == t["socio"]["nombre"]
