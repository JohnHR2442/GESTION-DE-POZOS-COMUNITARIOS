"""
Script para limpiar los datos de PRUEBA de la base de datos.

Borra por completo: recorridos, multas, emergencias, notificaciones y avisos.
Reinicia: las horas de agua de sobra de los socios a 0.
NO toca: usuarios (contrasenas) ni pozos.

Deja la base como "recien instalada" pero conservando tus usuarios y contrasenas.

Uso:
    cd backend
    python reset_pruebas.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "turnos_de_pozo")

if not MONGO_URL:
    raise SystemExit(
        "\nNo encontre MONGO_URL.\n"
        "Crea un archivo backend/.env con estas dos lineas:\n"
        "  MONGO_URL=mongodb+srv://usuario:password@cluster0.xxxx.mongodb.net/\n"
        "  DB_NAME=turnos_de_pozo\n"
    )

# Colecciones de PRUEBA que se vacian por completo
COLECCIONES_PRUEBA = [
    "dias_sin_servicio",  # recorridos (verde / rojo)
    "multas",
    "emergencias",
    "notificaciones",
    "festivo_avisos",
    "push_devices",
    "password_resets",
]


def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    print(f"\nConectado a la base: {DB_NAME}\n")

    for nombre in COLECCIONES_PRUEBA:
        res = db[nombre].delete_many({})
        print(f"  - {nombre}: {res.deleted_count} documentos borrados")

    # Reiniciar horas de agua de sobra a 0 (no afecta contrasenas)
    res = db.usuarios.update_many({}, {"$set": {"horas_sobra": 0}})
    print(f"\n  - horas_sobra reiniciadas a 0 en {res.modified_count} usuarios")

    print(
        "\nListo. Usuarios y contrasenas intactos. "
        "Base limpia para pruebas.\n"
    )
    client.close()


if __name__ == "__main__":
    main()
