import os
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
from typing import List, Optional, Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from jose import JWTError, jwt
from dotenv import load_dotenv
import bcrypt
import httpx
import secrets
import aiosmtplib
from email.message import EmailMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("turnos")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "turnos_de_pozo")
JWT_SECRET = os.environ.get("JWT_SECRET", "cambia-esta-clave-secreta")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7
DEFAULT_PASSWORD = "pozo2026"
SEASON_START = date(2026, 2, 1)

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
RESET_CODE_TTL_MIN = 15

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="Turnos de Pozo API")
api = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# Push notifications (servicio administrado por Emergent)
# ---------------------------------------------------------------------------
PUSH_BASE_URL = "https://integrations.emergentagent.com"
PUSH_KEY = os.environ.get("EMERGENT_PUSH_KEY", "placeholder")
_push_client = httpx.AsyncClient(
    base_url=PUSH_BASE_URL,
    headers={"X-Push-Key": PUSH_KEY},
    timeout=10.0,
)


async def send_push(recipients: List[str], titulo: str, mensaje: str):
    """Envia una push a una lista de user_id via el relay de Emergent."""
    recipients = [r for r in recipients if r]
    if not recipients:
        return
    for i in range(0, len(recipients), 100):
        chunk = recipients[i:i + 100]
        payload = {"recipients": chunk, "data": {"title": titulo, "message": mensaje}}
        resp = await _push_client.post("/api/v1/push/trigger", json=payload)
        resp.raise_for_status()


async def send_reset_email(socio_email: str, code: str):
    """Envia el codigo de recuperacion al correo del comisariado."""
    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS
    msg["Subject"] = f"Codigo de recuperacion - {socio_email}"
    msg.set_content(
        f"El socio {socio_email} solicito recuperar su contrasena.\n\n"
        f"Codigo de un solo uso: {code}\n"
        f"Vigencia: {RESET_CODE_TTL_MIN} minutos.\n\n"
        f"Entrega este codigo unicamente al socio que lo solicito."
    )
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=GMAIL_ADDRESS,
        password=GMAIL_APP_PASSWORD,
    )


# ---------------------------------------------------------------------------
# Mongo helpers
# ---------------------------------------------------------------------------
def to_str_id(value) -> str:
    if isinstance(value, ObjectId):
        return str(value)
    return str(value)


PyObjectId = Annotated[str, BeforeValidator(to_str_id)]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_token(user_id: str, rol: str, pozo_id: str) -> str:
    payload = {
        "sub": user_id,
        "rol": rol,
        "pozo_id": pozo_id,
        "iat": now_utc(),
        "exp": now_utc() + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# Holidays (festivos) including Computus (Easter) for any year
# ---------------------------------------------------------------------------
def computus(year: int) -> date:
    """Anonymous Gregorian algorithm for Easter Sunday."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def easter_holidays(year: int) -> List[str]:
    """Jueves Santo and Viernes Santo (Holy Thursday and Good Friday)."""
    easter = computus(year)
    jueves = easter - timedelta(days=3)
    viernes = easter - timedelta(days=2)
    return [jueves.strftime("%m-%d"), viernes.strftime("%m-%d")]


def festivos_for_year(base_festivos: List[str], year: int) -> List[str]:
    """Return list of YYYY-MM-DD strings for the given year."""
    result = []
    for md in base_festivos:
        result.append(f"{year}-{md}")
    for md in easter_holidays(year):
        result.append(f"{year}-{md}")
    return result


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class MultaCreate(BaseModel):
    socio_id: str
    descripcion: str
    monto: float
    fecha_creacion: Optional[str] = None  # YYYY-MM-DD


class MultaUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[float] = None
    socio_id: Optional[str] = None


class DiaSinServicioCreate(BaseModel):
    fecha: str  # YYYY-MM-DD
    motivo: Optional[str] = None


class EmergenciaCreate(BaseModel):
    tipo: str  # tuberia | hidrante | presion


class PushTokenRequest(BaseModel):
    token: str


class RegisterPushBody(BaseModel):
    user_id: str
    platform: str  # "android" | "ios"
    device_token: str


class ResetRequest(BaseModel):
    email: EmailStr


class ResetVerify(BaseModel):
    email: EmailStr
    code: str


class ResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(min_length=6)


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer(auto_error=False)


async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    if creds is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalido")
    user = await db.usuarios.find_one({"id": user_id})
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_contador(user=Depends(get_current_user)):
    if user["rol"] != "contador":
        raise HTTPException(status_code=403, detail="Solo el contador puede realizar esta accion")
    return user


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "nombre": user["nombre"],
        "email": user["email"],
        "telefono": user.get("telefono"),
        "rol": user["rol"],
        "pozo_id": user["pozo_id"],
        "orden": user.get("orden"),
    }


# ---------------------------------------------------------------------------
# Turn rotation logic
# ---------------------------------------------------------------------------
async def get_socios_ordenados(pozo_id: str) -> List[dict]:
    cursor = db.usuarios.find({"pozo_id": pozo_id, "rol": "socio"}).sort("orden", 1)
    return await cursor.to_list(length=20)


def pozo_inicio(pozo: dict) -> date:
    return date.fromisoformat(pozo.get("inicio", SEASON_START.isoformat()))


def socio_en_turno_index(target: date, start: date = SEASON_START) -> int:
    if target < start:
        return -1
    delta = (target - start).days
    return delta % 9


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
POZOS_SEED = [
    {
        "id": "isidro",
        "nombre": "San Isidro",
        "dominio": "isidro.com",
        "accent": "#0EA5E9",
        "inicio": "2026-01-06",
        "festivos": ["01-01", "02-12", "03-19", "05-15", "09-15", "11-01", "11-02", "12-12", "12-25"],
        "socios": [
            ("Alfredo Velez", "2231159370", "alfredo.velez@isidro.com"),
            ("Simon Meneses", "2231223120", "simon.meneses@isidro.com"),
            ("Francisco Meneses", "2231265651", "francisco.meneses@isidro.com"),
            ("Jose Isabel Huerta", "2231162273", "jose.huerta@isidro.com"),
            ("Marcelino Huerta", "2231927351", "marcelino.huerta@isidro.com"),
            ("Sidoro Meneses", "2231010234", "sidoro.meneses@isidro.com"),
            ("Lilian Ramirez", "2231551123", "lilian.ramirez@isidro.com"),
            ("Freddy Garcia", "2231814573", "freddy.garcia@isidro.com"),
            ("Freddy Rojas", "2231123475", "freddy.rojas@isidro.com"),
        ],
    },
    {
        "id": "zapata",
        "nombre": "Zapata",
        "dominio": "zapata.com",
        "accent": "#10B981",
        "inicio": "2026-02-01",
        "festivos": ["01-01", "02-12", "03-19", "08-08", "09-15", "11-01", "11-02", "12-12", "12-25"],
        "socios": [
            ("Jorge Velez", "2231152247", "jorge.velez@zapata.com"),
            ("Josefa Zavaleta", "2231223132", "josefa.zavaleta@zapata.com"),
            ("Ivan Meneses", "2231265576", "ivan.meneses@zapata.com"),
            ("Isael Gil", "2231164774", "isael.gil@zapata.com"),
            ("Jorge Rojas", "2231921152", "jorge.rojas@zapata.com"),
            ("Alexander Rojas", "2231019885", "alexander.rojas@zapata.com"),
            ("Angel Perez", "2231551324", "angel.perez@zapata.com"),
            ("Freddy Garcia", "2231816614", "freddy.garcia@zapata.com"),
            ("Oscar Meneses", "2231122442", "oscar.meneses@zapata.com"),
        ],
    },
    {
        "id": "cardenas",
        "nombre": "Cardenas",
        "dominio": "cardenas.com",
        "accent": "#F59E0B",
        "inicio": "2026-02-01",
        "festivos": ["01-01", "02-12", "03-19", "05-21", "09-15", "11-01", "11-02", "12-12", "12-25"],
        "socios": [
            ("Antonio Jimenez", "2231153256", "antonio.jimenez@cardenas.com"),
            ("Manuel Meneses", "2231221984", "manuel.meneses@cardenas.com"),
            ("Alan Huerta", "2231266891", "alan.huerta@cardenas.com"),
            ("Gabino Huerta", "2231165456", "gabino.huerta@cardenas.com"),
            ("David Velez", "2231921199", "david.velez@cardenas.com"),
            ("Ismael Rojas", "2231014554", "ismael.rojas@cardenas.com"),
            ("Dario Duran", "2231556879", "dario.duran@cardenas.com"),
            ("Francisco Rojas", "2231811215", "francisco.rojas@cardenas.com"),
            ("Edwin Jeronimo", "2231126354", "edwin.jeronimo@cardenas.com"),
        ],
    },
]


async def seed_database():
    default_hash = hash_password(DEFAULT_PASSWORD)
    for pozo in POZOS_SEED:
        # Metadatos del pozo: siempre se sincronizan (idempotente), asi el
        # campo "inicio" queda actualizado aunque los usuarios ya existan.
        await db.pozos.update_one(
            {"id": pozo["id"]},
            {"$set": {
                "id": pozo["id"],
                "nombre": pozo["nombre"],
                "dominio": pozo["dominio"],
                "accent": pozo["accent"],
                "festivos": pozo["festivos"],
                "inicio": pozo["inicio"],
            }},
            upsert=True,
        )
        # contador
        contador_email = f"contador@{pozo['dominio']}"
        if not await db.usuarios.find_one({"email": contador_email}):
            await db.usuarios.insert_one({
                "id": str(uuid.uuid4()),
                "pozo_id": pozo["id"],
                "nombre": f"Contador {pozo['nombre']}",
                "email": contador_email,
                "telefono": None,
                "rol": "contador",
                "orden": None,
                "hashed_password": default_hash,
                "is_active": True,
                "push_token": None,
            })
        # socios
        for idx, (nombre, telefono, email) in enumerate(pozo["socios"], start=1):
            if not await db.usuarios.find_one({"email": email}):
                await db.usuarios.insert_one({
                    "id": str(uuid.uuid4()),
                    "pozo_id": pozo["id"],
                    "nombre": nombre,
                    "email": email,
                    "telefono": telefono,
                    "rol": "socio",
                    "orden": idx,
                    "hashed_password": default_hash,
                    "is_active": True,
                    "push_token": None,
                })
    logger.info("Seed: base de datos inicializada")


# ---------------------------------------------------------------------------
# Notification helper
# ---------------------------------------------------------------------------
async def crear_notificacion(pozo_id: str, tipo: str, titulo: str, mensaje: str, destinatario: str = "todos"):
    doc = {
        "id": str(uuid.uuid4()),
        "pozo_id": pozo_id,
        "tipo": tipo,
        "titulo": titulo,
        "mensaje": mensaje,
        "destinatario": destinatario,  # "todos" o socio_id
        "fecha": now_utc().isoformat(),
        "leida_por": [],
    }
    await db.notificaciones.insert_one(doc)
    # Envio de push (no bloquea la operacion principal si falla)
    try:
        if destinatario == "todos":
            users = await db.usuarios.find({"pozo_id": pozo_id}).to_list(length=50)
            recipients = [u["id"] for u in users]
        else:
            recipients = [destinatario]
        await send_push(recipients, titulo, mensaje)
    except Exception as e:
        logger.warning(f"Push fallo (no bloqueante): {e}")
    return doc


def clean(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


# ---------------------------------------------------------------------------
# Routes: Auth
# ---------------------------------------------------------------------------
@api.post("/auth/login")
async def login(req: LoginRequest):
    email = req.email.lower().strip()
    user = await db.usuarios.find_one({"email": email})
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Correo o contrasena incorrectos")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    token = create_token(user["id"], user["rol"], user["pozo_id"])
    pozo = await db.pozos.find_one({"id": user["pozo_id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": public_user(user),
        "pozo": clean(pozo) if pozo else None,
    }


@api.get("/auth/me")
async def me(user=Depends(get_current_user)):
    pozo = await db.pozos.find_one({"id": user["pozo_id"]})
    return {"user": public_user(user), "pozo": clean(pozo) if pozo else None}


@api.post("/auth/change-password")
async def change_password(req: ChangePasswordRequest, user=Depends(get_current_user)):
    if not verify_password(req.current_password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="La contrasena actual es incorrecta")
    await db.usuarios.update_one(
        {"id": user["id"]},
        {"$set": {"hashed_password": hash_password(req.new_password)}},
    )
    return {"detail": "Contrasena actualizada correctamente"}


@api.post("/auth/push-token")
async def save_push_token(req: PushTokenRequest, user=Depends(get_current_user)):
    await db.usuarios.update_one({"id": user["id"]}, {"$set": {"push_token": req.token}})
    return {"detail": "Token guardado"}


@api.post("/register-push", status_code=201)
async def register_push(body: RegisterPushBody):
    resp = await _push_client.post("/api/v1/push/users/register", json=body.model_dump())
    if resp.status_code == 401:
        raise HTTPException(500, "EMERGENT_PUSH_KEY faltante o invalida")
    if resp.status_code >= 500:
        raise HTTPException(502, "Servicio de push no disponible")
    resp.raise_for_status()
    return {"status": "registered"}


async def _find_valid_reset(email: str, code: str):
    doc = await db.password_resets.find_one({"email": email, "used": False})
    if not doc:
        return None
    expires = datetime.fromisoformat(doc["expires_at"])
    if expires < now_utc():
        return None
    if not verify_password(code, doc["code_hash"]):
        return None
    return doc


@api.post("/auth/reset/request")
async def reset_request(req: ResetRequest):
    email = req.email.lower().strip()
    user = await db.usuarios.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Ese correo no esta registrado")
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise HTTPException(status_code=500, detail="El correo de recuperacion no esta configurado")
    # invalida codigos previos
    await db.password_resets.delete_many({"email": email})
    code = f"{secrets.randbelow(10 ** 6):06d}"
    doc = {
        "email": email,
        "code_hash": hash_password(code),
        "expires_at": (now_utc() + timedelta(minutes=RESET_CODE_TTL_MIN)).isoformat(),
        "used": False,
        "created_at": now_utc().isoformat(),
    }
    await db.password_resets.insert_one(doc)
    try:
        await send_reset_email(email, code)
    except Exception as e:
        logger.error(f"Error enviando correo de recuperacion: {e}")
        raise HTTPException(status_code=502, detail="No se pudo enviar el codigo. Intenta de nuevo.")
    return {"detail": "Se envio un codigo al comisariado."}


@api.post("/auth/reset/verify")
async def reset_verify(req: ResetVerify):
    email = req.email.lower().strip()
    doc = await _find_valid_reset(email, req.code.strip())
    if not doc:
        raise HTTPException(status_code=400, detail="Codigo invalido o expirado")
    return {"valid": True}


@api.post("/auth/reset/confirm")
async def reset_confirm(req: ResetConfirm):
    email = req.email.lower().strip()
    doc = await _find_valid_reset(email, req.code.strip())
    if not doc:
        raise HTTPException(status_code=400, detail="Codigo invalido o expirado")
    await db.usuarios.update_one(
        {"email": email},
        {"$set": {"hashed_password": hash_password(req.new_password)}},
    )
    await db.password_resets.delete_many({"email": email})
    return {"detail": "Contrasena actualizada. Ya puedes iniciar sesion."}


# ---------------------------------------------------------------------------
# Routes: Pozos (public)
# ---------------------------------------------------------------------------
@api.get("/pozos")
async def list_pozos():
    cursor = db.pozos.find({})
    pozos = await cursor.to_list(length=10)
    return [clean(p) for p in pozos]


@api.get("/pozos/{pozo_id}/socios")
async def public_socios(pozo_id: str):
    socios = await get_socios_ordenados(pozo_id)
    if not socios:
        raise HTTPException(status_code=404, detail="Pozo no encontrado")
    pozo = await db.pozos.find_one({"id": pozo_id})
    turno_idx = socio_en_turno_index(date.today(), pozo_inicio(pozo))
    result = []
    for s in socios:
        en_turno = (s.get("orden") == turno_idx + 1) if turno_idx >= 0 else False
        result.append({
            "id": s["id"],
            "nombre": s["nombre"],
            "telefono": s.get("telefono"),
            "orden": s.get("orden"),
            "en_turno": en_turno,
        })
    return result


@api.get("/pozos/{pozo_id}/turno-hoy")
async def turno_hoy(pozo_id: str):
    socios = await get_socios_ordenados(pozo_id)
    if not socios:
        raise HTTPException(status_code=404, detail="Pozo no encontrado")
    pozo = await db.pozos.find_one({"id": pozo_id})
    idx = socio_en_turno_index(date.today(), pozo_inicio(pozo))
    if idx < 0:
        return {"socio": None, "fecha": date.today().isoformat()}
    socio = next((s for s in socios if s.get("orden") == idx + 1), None)
    return {
        "socio": {"id": socio["id"], "nombre": socio["nombre"]} if socio else None,
        "fecha": date.today().isoformat(),
    }


# ---------------------------------------------------------------------------
# Routes: Turnos / Calendario
# ---------------------------------------------------------------------------
@api.get("/turnos/calendario")
async def calendario(year: int, month: int, user=Depends(get_current_user)):
    pozo_id = user["pozo_id"]
    socios = await get_socios_ordenados(pozo_id)
    pozo = await db.pozos.find_one({"id": pozo_id})
    festivos = set(festivos_for_year(pozo.get("festivos", []), year))
    inicio = pozo_inicio(pozo)
    # dias sin servicio (manual)
    dss_cursor = db.dias_sin_servicio.find({"pozo_id": pozo_id})
    dss_docs = await dss_cursor.to_list(length=500)
    dias_sin = {d["fecha"]: d.get("motivo") for d in dss_docs}

    # build days in month
    d = date(year, month, 1)
    dias = []
    while d.month == month:
        idx = socio_en_turno_index(d, inicio)
        socio = next((s for s in socios if s.get("orden") == idx + 1), None) if idx >= 0 else None
        iso = d.isoformat()
        es_festivo = iso in festivos
        es_sin_servicio = iso in dias_sin
        dias.append({
            "fecha": iso,
            "dia": d.day,
            "socio_id": socio["id"] if socio else None,
            "socio_nombre": socio["nombre"] if socio else None,
            "festivo": es_festivo,
            "sin_servicio": es_sin_servicio,
            "motivo": dias_sin.get(iso),
        })
        d = d + timedelta(days=1)
    return {"year": year, "month": month, "dias": dias, "accent": pozo.get("accent")}


# ---------------------------------------------------------------------------
# Routes: Recorrido / Dias sin servicio
# ---------------------------------------------------------------------------
@api.get("/dias-sin-servicio")
async def list_dias_sin_servicio(user=Depends(get_current_user)):
    cursor = db.dias_sin_servicio.find({"pozo_id": user["pozo_id"]})
    docs = await cursor.to_list(length=1000)
    return [clean(d) for d in docs]


@api.post("/dias-sin-servicio")
async def crear_dia_sin_servicio(req: DiaSinServicioCreate, user=Depends(get_current_user)):
    existing = await db.dias_sin_servicio.find_one({"pozo_id": user["pozo_id"], "fecha": req.fecha})
    if existing:
        raise HTTPException(status_code=400, detail="Ese dia ya esta marcado sin servicio")
    doc = {
        "id": str(uuid.uuid4()),
        "pozo_id": user["pozo_id"],
        "fecha": req.fecha,
        "motivo": req.motivo or "Dia sin servicio",
        "creado_por": user["nombre"],
        "creado_en": now_utc().isoformat(),
    }
    await db.dias_sin_servicio.insert_one(doc)
    await crear_notificacion(
        user["pozo_id"], "sin_servicio", "Dia sin servicio",
        f"{user['nombre']} marco el {req.fecha} como dia sin servicio.",
    )
    return clean(doc)


@api.delete("/dias-sin-servicio/{dss_id}")
async def borrar_dia_sin_servicio(dss_id: str, user=Depends(get_current_user)):
    res = await db.dias_sin_servicio.delete_one({"id": dss_id, "pozo_id": user["pozo_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"detail": "Eliminado"}


# ---------------------------------------------------------------------------
# Routes: Emergencias
# ---------------------------------------------------------------------------
EMERGENCIA_LABELS = {
    "tuberia": "Fuga en tuberia",
    "hidrante": "Problema en hidrante",
    "presion": "Baja presion de agua",
}


@api.post("/emergencias")
async def crear_emergencia(req: EmergenciaCreate, user=Depends(get_current_user)):
    if req.tipo not in EMERGENCIA_LABELS:
        raise HTTPException(status_code=400, detail="Tipo de emergencia invalido")
    doc = {
        "id": str(uuid.uuid4()),
        "pozo_id": user["pozo_id"],
        "tipo": req.tipo,
        "etiqueta": EMERGENCIA_LABELS[req.tipo],
        "socio_id": user["id"],
        "socio_nombre": user["nombre"],
        "fecha": now_utc().isoformat(),
    }
    await db.emergencias.insert_one(doc)
    await crear_notificacion(
        user["pozo_id"], "emergencia", "Emergencia reportada",
        f"{user['nombre']} reporto: {EMERGENCIA_LABELS[req.tipo]}.",
    )
    return clean(doc)


@api.get("/emergencias")
async def list_emergencias(user=Depends(get_current_user)):
    cursor = db.emergencias.find({"pozo_id": user["pozo_id"]}).sort("fecha", -1)
    docs = await cursor.to_list(length=200)
    return [clean(d) for d in docs]


# ---------------------------------------------------------------------------
# Routes: Multas
# ---------------------------------------------------------------------------
@api.get("/multas")
async def list_multas(user=Depends(get_current_user)):
    cursor = db.multas.find({"pozo_id": user["pozo_id"]}).sort("fecha_creacion", -1)
    docs = await cursor.to_list(length=1000)
    return [clean(d) for d in docs]


@api.get("/multas/mias")
async def list_mis_multas(user=Depends(get_current_user)):
    cursor = db.multas.find({"pozo_id": user["pozo_id"], "socio_id": user["id"]}).sort("fecha_creacion", -1)
    docs = await cursor.to_list(length=1000)
    return [clean(d) for d in docs]


@api.post("/multas")
async def crear_multa(req: MultaCreate, user=Depends(require_contador)):
    socio = await db.usuarios.find_one({"id": req.socio_id, "pozo_id": user["pozo_id"], "rol": "socio"})
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado en este pozo")
    fecha_creacion = req.fecha_creacion or date.today().isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "pozo_id": user["pozo_id"],
        "socio_id": socio["id"],
        "socio_nombre": socio["nombre"],
        "descripcion": req.descripcion,
        "monto": round(float(req.monto), 2),
        "estado": "no_pagado",
        "fecha_creacion": fecha_creacion,
        "fecha_pago": None,
    }
    await db.multas.insert_one(doc)
    await crear_notificacion(
        user["pozo_id"], "multa",
        "Nueva multa registrada",
        f"Se te asigno una multa de ${doc['monto']:,.2f} MXN: {req.descripcion}.",
        destinatario=socio["id"],
    )
    return clean(doc)


@api.patch("/multas/{multa_id}")
async def editar_multa(multa_id: str, req: MultaUpdate, user=Depends(require_contador)):
    multa = await db.multas.find_one({"id": multa_id, "pozo_id": user["pozo_id"]})
    if not multa:
        raise HTTPException(status_code=404, detail="Multa no encontrada")
    updates = {}
    if req.descripcion is not None:
        updates["descripcion"] = req.descripcion
    if req.monto is not None:
        updates["monto"] = round(float(req.monto), 2)
    if req.socio_id is not None:
        socio = await db.usuarios.find_one({"id": req.socio_id, "pozo_id": user["pozo_id"], "rol": "socio"})
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        updates["socio_id"] = socio["id"]
        updates["socio_nombre"] = socio["nombre"]
    if updates:
        await db.multas.update_one({"id": multa_id}, {"$set": updates})
    updated = await db.multas.find_one({"id": multa_id})
    return clean(updated)


@api.post("/multas/{multa_id}/pagar")
async def pagar_multa(multa_id: str, user=Depends(require_contador)):
    multa = await db.multas.find_one({"id": multa_id, "pozo_id": user["pozo_id"]})
    if not multa:
        raise HTTPException(status_code=404, detail="Multa no encontrada")
    await db.multas.update_one(
        {"id": multa_id},
        {"$set": {"estado": "pagado", "fecha_pago": date.today().isoformat()}},
    )
    updated = await db.multas.find_one({"id": multa_id})
    return clean(updated)


@api.delete("/multas/{multa_id}")
async def borrar_multa(multa_id: str, user=Depends(require_contador)):
    res = await db.multas.delete_one({"id": multa_id, "pozo_id": user["pozo_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Multa no encontrada")
    return {"detail": "Multa eliminada"}


@api.get("/socios")
async def list_socios(user=Depends(get_current_user)):
    socios = await get_socios_ordenados(user["pozo_id"])
    return [{"id": s["id"], "nombre": s["nombre"], "orden": s.get("orden")} for s in socios]


# ---------------------------------------------------------------------------
# Routes: Notificaciones
# ---------------------------------------------------------------------------
def notif_visible_para(notif: dict, user: dict) -> bool:
    dest = notif.get("destinatario", "todos")
    return dest == "todos" or dest == user["id"]


@api.get("/notificaciones")
async def list_notificaciones(user=Depends(get_current_user)):
    cursor = db.notificaciones.find({"pozo_id": user["pozo_id"]}).sort("fecha", -1)
    docs = await cursor.to_list(length=200)
    visibles = [d for d in docs if notif_visible_para(d, user)]
    result = []
    for d in visibles:
        d = clean(d)
        d["leida"] = user["id"] in d.get("leida_por", [])
        result.append(d)
    return result


@api.get("/notificaciones/pendientes")
async def notificaciones_pendientes(since: Optional[str] = None, user=Depends(get_current_user)):
    query = {"pozo_id": user["pozo_id"]}
    if since:
        query["fecha"] = {"$gt": since}
    cursor = db.notificaciones.find(query).sort("fecha", -1)
    docs = await cursor.to_list(length=100)
    visibles = [clean(d) for d in docs if notif_visible_para(d, user)]
    no_leidas = [d for d in visibles if user["id"] not in d.get("leida_por", [])]
    return {
        "pendientes": visibles,
        "no_leidas": len(no_leidas),
        "server_time": now_utc().isoformat(),
    }


@api.post("/notificaciones/{notif_id}/leer")
async def marcar_leida(notif_id: str, user=Depends(get_current_user)):
    await db.notificaciones.update_one(
        {"id": notif_id, "pozo_id": user["pozo_id"]},
        {"$addToSet": {"leida_por": user["id"]}},
    )
    return {"detail": "Marcada como leida"}


@api.post("/notificaciones/leer-todas")
async def marcar_todas(user=Depends(get_current_user)):
    cursor = db.notificaciones.find({"pozo_id": user["pozo_id"]})
    docs = await cursor.to_list(length=500)
    for d in docs:
        if notif_visible_para(d, user):
            await db.notificaciones.update_one(
                {"id": d["id"]}, {"$addToSet": {"leida_por": user["id"]}}
            )
    return {"detail": "Todas marcadas como leidas"}


# ---------------------------------------------------------------------------
# Routes: Estadisticas
# ---------------------------------------------------------------------------
@api.get("/estadisticas")
async def estadisticas(user=Depends(get_current_user)):
    pozo_id = user["pozo_id"]
    multas = await db.multas.find({"pozo_id": pozo_id}).to_list(length=2000)
    total_multas = len(multas)
    pagadas = [m for m in multas if m.get("estado") == "pagado"]
    no_pagadas = [m for m in multas if m.get("estado") != "pagado"]
    monto_total = sum(m.get("monto", 0) for m in multas)
    monto_pagado = sum(m.get("monto", 0) for m in pagadas)
    monto_pendiente = sum(m.get("monto", 0) for m in no_pagadas)

    # multas del socio actual
    mis_multas = [m for m in multas if m.get("socio_id") == user["id"]]

    # turnos del socio en el ano actual (conteo aproximado de dias asignados)
    mis_turnos = 0
    if user.get("orden"):
        pozo = await db.pozos.find_one({"id": pozo_id})
        inicio = pozo_inicio(pozo)
        d = inicio
        end = date(inicio.year, 12, 31)
        while d <= end:
            if socio_en_turno_index(d, inicio) == user["orden"] - 1:
                mis_turnos += 1
            d += timedelta(days=1)

    emergencias = await db.emergencias.count_documents({"pozo_id": pozo_id})
    dias_sin = await db.dias_sin_servicio.count_documents({"pozo_id": pozo_id})

    # multas por socio (para grafica)
    socios = await get_socios_ordenados(pozo_id)
    por_socio = []
    for s in socios:
        count = sum(1 for m in multas if m.get("socio_id") == s["id"])
        por_socio.append({"nombre": s["nombre"], "orden": s.get("orden"), "multas": count})

    return {
        "total_multas": total_multas,
        "multas_pagadas": len(pagadas),
        "multas_no_pagadas": len(no_pagadas),
        "monto_total": round(monto_total, 2),
        "monto_pagado": round(monto_pagado, 2),
        "monto_pendiente": round(monto_pendiente, 2),
        "mis_multas": len(mis_multas),
        "mis_turnos": mis_turnos,
        "emergencias": emergencias,
        "dias_sin_servicio": dias_sin,
        "por_socio": por_socio,
    }


# ---------------------------------------------------------------------------
# Routes: Historial (turnos del socio por mes)
# ---------------------------------------------------------------------------
@api.get("/historial")
async def historial(year: int, month: int, user=Depends(get_current_user)):
    pozo = await db.pozos.find_one({"id": user["pozo_id"]})
    festivos = set(festivos_for_year(pozo.get("festivos", []), year))
    inicio = pozo_inicio(pozo)
    dss_docs = await db.dias_sin_servicio.find({"pozo_id": user["pozo_id"]}).to_list(length=500)
    dias_sin = {d["fecha"]: d.get("motivo") for d in dss_docs}
    orden = user.get("orden")
    dias = []
    if orden:
        d = date(year, month, 1)
        while d.month == month:
            if socio_en_turno_index(d, inicio) == orden - 1:
                iso = d.isoformat()
                dias.append({
                    "fecha": iso,
                    "dia": d.day,
                    "festivo": iso in festivos,
                    "sin_servicio": iso in dias_sin,
                })
            d += timedelta(days=1)
    return {"year": year, "month": month, "dias": dias, "socio": user["nombre"]}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@api.get("/")
async def root():
    return {"message": "Turnos de Pozo API", "status": "ok"}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await db.usuarios.create_index("email", unique=True)
    await db.usuarios.create_index("pozo_id")
    await db.multas.create_index("pozo_id")
    await seed_database()


@app.on_event("shutdown")
async def on_shutdown():
    client.close()
