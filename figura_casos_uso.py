# -*- coding: utf-8 -*-
"""Genera la Figura 3.1 - Diagrama de casos de uso."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle

AZUL = "#0284C7"
GRIS = "#334155"

fig, ax = plt.subplots(figsize=(12, 8.5), dpi=160)
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis("off")


def actor(x, y, nombre):
    # cabeza
    ax.add_patch(plt.Circle((x, y + 0.55), 0.22, fill=False, lw=2, color=GRIS))
    # cuerpo
    ax.plot([x, x], [y + 0.33, y - 0.25], color=GRIS, lw=2)
    # brazos
    ax.plot([x - 0.35, x + 0.35], [y + 0.15, y + 0.15], color=GRIS, lw=2)
    # piernas
    ax.plot([x, x - 0.3], [y - 0.25, y - 0.7], color=GRIS, lw=2)
    ax.plot([x, x + 0.3], [y - 0.25, y - 0.7], color=GRIS, lw=2)
    ax.text(x, y - 1.0, nombre, ha="center", va="center",
            fontsize=12, fontweight="bold", color=GRIS)


def caso(x, y, texto, w=2.5, h=0.95):
    ax.add_patch(Ellipse((x, y), w, h, fill=True, facecolor="#E0F2FE",
                         edgecolor=AZUL, lw=1.8))
    ax.text(x, y, texto, ha="center", va="center", fontsize=8.3,
            color="#0C4A6E", wrap=True)
    return (x, y, w, h)


def liga(actor_xy, caso_xy, lado="der"):
    ax0, ay0 = actor_xy
    cx, cy, cw, ch = caso_xy
    borde = cx - cw / 2 if lado == "izq" else cx + cw / 2
    ax.plot([ax0, borde], [ay0, cy], color="#94A3B8", lw=1.1, zorder=0)


# Sistema (límite)
ax.add_patch(Rectangle((2.7, 0.4), 6.6, 9.2, fill=False, edgecolor=GRIS, lw=1.6))
ax.text(6.0, 9.85, "Sistema: Gestión de Pozos Comunitarios",
        ha="center", va="center", fontsize=12, fontweight="bold", color=GRIS)

# Actores
soc = (0.95, 5.0)
con = (11.05, 5.0)
actor(*soc, "Socio")
actor(*con, "Contador")

# Casos de uso compartidos (centro)
c_login = caso(6.0, 8.7, "Iniciar sesión")
c_pass = caso(6.0, 1.2, "Recuperar contraseña")

# Casos de uso del Socio (columna izquierda)
c_turno = caso(4.55, 7.4, "Consultar turno\n(calendario)")
c_vmul = caso(4.55, 6.1, "Ver mis multas")
c_emer = caso(4.55, 4.8, "Reportar\nemergencia")
c_agua = caso(4.55, 3.5, "Registrar\nagua de sobra")

# Casos de uso del Contador (columna derecha)
c_amul = caso(7.45, 7.4, "Administrar\nmultas")
c_dsin = caso(7.45, 5.9, "Registrar días sin\nservicio y recorridos", w=2.7)
c_stats = caso(7.45, 4.3, "Consultar\nestadísticas")

# Ligas Socio
for c in (c_login, c_turno, c_vmul, c_emer, c_agua, c_pass):
    liga(soc, c, "izq")

# Ligas Contador
for c in (c_login, c_amul, c_dsin, c_stats, c_pass):
    liga(con, c, "der")

plt.tight_layout()
plt.savefig("/app/figura_3_1.png", bbox_inches="tight", facecolor="white")
print("OK -> /app/figura_3_1.png")
