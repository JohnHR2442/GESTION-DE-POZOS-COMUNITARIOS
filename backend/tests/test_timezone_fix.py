"""
Tests for the timezone bug fix on pozo 'isidro'.

Bug: /api/pozos/isidro/turno-hoy y /api/pozos/isidro/socios calculaban 'hoy'
en UTC. De noche en Mexico (UTC-6) UTC ya es el dia siguiente, por lo que la
API adelantaba el turno un dia (Marcelino Huerta en vez de Jose Isabel Huerta).

Fix: se agrego today_local() con TZ UTC-6 y se reemplazaron todos los
date.today() por today_local() en el server.

Estos tests se ejecutan contra el backend LOCAL (localhost:8001/api).
"""

from datetime import date, datetime, timedelta, timezone

import pytest
import requests

BASE_URL = "http://localhost:8001/api"

LOCAL_TZ = timezone(timedelta(hours=-6))


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _local_today() -> date:
    return datetime.now(LOCAL_TZ).date()


# Turno correcto que debe estar activo el 2026-09-20 (domingo local Mexico).
# inicio pozo isidro = 2026-01-08 -> (2026-09-20 - 2026-01-08).days % 9 = 3
# orden = idx + 1 = 4 = "Jose Isabel Huerta"
def _expected_socio_for(target: date) -> int:
    inicio = date(2026, 1, 8)
    return ((target - inicio).days % 9) + 1


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------------------------------------------------------------------
# Timezone bug fix
# ---------------------------------------------------------------------------
class TestTurnoHoyTimezone:
    def test_discrepancy_exists(self):
        """Sanity check: existe discrepancia real UTC vs UTC-6 al momento del test."""
        utc = _utc_today()
        local = _local_today()
        print(f"UTC today={utc.isoformat()} | Mexico(UTC-6) today={local.isoformat()}")
        # No es requisito estricto, pero informamos si no hay discrepancia.
        if utc == local:
            pytest.skip("No hay discrepancia UTC vs UTC-6 en este momento; test no discriminatorio.")

    def test_turno_hoy_returns_local_date(self, api):
        r = api.get(f"{BASE_URL}/pozos/isidro/turno-hoy")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "fecha" in data
        local = _local_today().isoformat()
        utc = _utc_today().isoformat()
        assert data["fecha"] == local, (
            f"turno-hoy fecha={data['fecha']} debe ser LOCAL ({local}), no UTC ({utc})"
        )
        if utc != local:
            assert data["fecha"] != utc, "La API todavia devuelve la fecha UTC (fix no aplicado)"

    def test_turno_hoy_socio_matches_local(self, api):
        r = api.get(f"{BASE_URL}/pozos/isidro/turno-hoy")
        assert r.status_code == 200
        data = r.json()
        assert data.get("socio") is not None
        # Debe ser el socio del dia LOCAL
        local = _local_today()
        expected_orden = _expected_socio_for(local)
        # Buscar el socio para comparar nombre/orden
        r2 = api.get(f"{BASE_URL}/pozos/isidro/socios")
        assert r2.status_code == 200
        socios = r2.json()
        expected = next(s for s in socios if s["orden"] == expected_orden)
        assert data["socio"]["nombre"] == expected["nombre"], (
            f"turno-hoy socio={data['socio']['nombre']} debe ser {expected['nombre']} "
            f"(orden {expected_orden}) para fecha local {local.isoformat()}"
        )
        # Con la discrepancia actual esperamos concretamente Jose Isabel Huerta
        if local == date(2026, 9, 20):
            assert data["socio"]["nombre"] == "Jose Isabel Huerta"

    def test_socios_en_turno_matches_local(self, api):
        r = api.get(f"{BASE_URL}/pozos/isidro/socios")
        assert r.status_code == 200
        socios = r.json()
        en_turno = [s for s in socios if s.get("en_turno")]
        assert len(en_turno) == 1, f"Debe haber exactamente 1 socio en turno, hay {len(en_turno)}"
        local = _local_today()
        expected_orden = _expected_socio_for(local)
        assert en_turno[0]["orden"] == expected_orden, (
            f"en_turno orden={en_turno[0]['orden']} debe ser {expected_orden} para fecha local"
        )
        # Con la discrepancia actual: NO debe ser Marcelino (orden 5)
        if local == date(2026, 9, 20):
            assert en_turno[0]["nombre"] == "Jose Isabel Huerta"
            assert en_turno[0]["orden"] == 4
            assert en_turno[0]["nombre"] != "Marcelino Huerta"


# ---------------------------------------------------------------------------
# Regression: endpoints no afectados siguen respondiendo 200
# ---------------------------------------------------------------------------
class TestRegression:
    def test_list_pozos(self, api):
        r = api.get(f"{BASE_URL}/pozos")
        assert r.status_code == 200
        pozos = r.json()
        assert isinstance(pozos, list) and len(pozos) >= 3
        ids = {p["id"] for p in pozos}
        assert {"isidro", "zapata", "cardenas"}.issubset(ids)

    def test_login_contador_isidro(self, api):
        r = api.post(
            f"{BASE_URL}/auth/login",
            json={"email": "contador@isidro.com", "password": "pozo2026"},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "access_token" in data
        assert data["user"]["rol"] == "contador"
        assert data["user"]["pozo_id"] == "isidro"
        # Guardamos el token para el siguiente test
        pytest.contador_token = data["access_token"]

    def test_calendario_septiembre_2026(self, api):
        token = getattr(pytest, "contador_token", None)
        if not token:
            # login inline si el orden cambia
            lr = api.post(
                f"{BASE_URL}/auth/login",
                json={"email": "contador@isidro.com", "password": "pozo2026"},
            )
            assert lr.status_code == 200
            token = lr.json()["access_token"]
        r = api.get(
            f"{BASE_URL}/turnos/calendario?year=2026&month=9",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["year"] == 2026 and data["month"] == 9
        assert isinstance(data["dias"], list) and len(data["dias"]) == 30
        # El dia 20 de septiembre debe corresponder a Jose Isabel Huerta (orden 4)
        d20 = next(d for d in data["dias"] if d["fecha"] == "2026-09-20")
        assert d20["socio_nombre"] == "Jose Isabel Huerta"
        d21 = next(d for d in data["dias"] if d["fecha"] == "2026-09-21")
        assert d21["socio_nombre"] == "Marcelino Huerta"
