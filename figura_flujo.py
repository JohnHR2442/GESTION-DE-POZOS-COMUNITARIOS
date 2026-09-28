# -*- coding: utf-8 -*-
"""Genera la Figura 3.2 - Diagrama de flujo del calculo del turno."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse

AZUL = "#0284C7"
AZULC = "#E0F2FE"
VERDE = "#16A34A"
GRIS = "#0C4A6E"

fig, ax = plt.subplots(figsize=(9, 13), dpi=155)
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis("off")


def flecha(x1, y1, x2, y2, texto="", color="#475569"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))
    if texto:
        ax.text((x1 + x2) / 2 + 0.25, (y1 + y2) / 2, texto,
                fontsize=10, fontweight="bold", color=color)


def proceso(x, y, texto, w=4.6, h=0.95):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.02", facecolor=AZULC,
                 edgecolor=AZUL, lw=1.8))
    ax.text(x, y, texto, ha="center", va="center", fontsize=9.2, color=GRIS)


def terminal(x, y, texto):
    ax.add_patch(Ellipse((x, y), 2.4, 0.9, facecolor=AZUL, edgecolor=AZUL))
    ax.text(x, y, texto, ha="center", va="center", fontsize=10,
            fontweight="bold", color="white")


def decision(x, y, texto, w=2.9, h=1.5):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="#FEF9C3",
                 edgecolor="#CA8A04", lw=1.8))
    ax.text(x, y, texto, ha="center", va="center", fontsize=8.8,
            fontweight="bold", color="#713F12")


def salida(x, y, texto, w=4.2, h=0.95):
    s = 0.5
    pts = [(x - w / 2 + s, y - h / 2), (x + w / 2, y - h / 2),
           (x + w / 2 - s, y + h / 2), (x - w / 2, y + h / 2)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="#DCFCE7",
                 edgecolor=VERDE, lw=1.8))
    ax.text(x, y, texto, ha="center", va="center", fontsize=9, color="#14532D")


# Nodos
terminal(5, 13.3, "INICIO")
proceso(5, 12.0, "Obtener fecha y hora local (UTC-6)")
decision(5, 10.3, "¿Hora actual\n≥ 18:00?")
proceso(8.0, 10.3, "fecha_efectiva =\nfecha + 1 día", w=3.3)
proceso(2.0, 10.3, "fecha_efectiva =\nfecha actual", w=3.3)
proceso(5, 8.4, "Calcular días transcurridos\n(fecha_efectiva − inicio_rotación)")
proceso(5, 6.9, "Restar festivos y días sin\nservicio → días válidos")
proceso(5, 5.4, "índice = días_válidos\nmód total_de_socios")
proceso(5, 3.9, "turno = lista_socios[índice]")
salida(5, 2.5, "Mostrar el turno del día")
terminal(5, 1.2, "FIN")

# Flechas
flecha(5, 12.85, 5, 12.5)          # inicio -> obtener fecha
flecha(5, 11.5, 5, 11.05)          # obtener -> decision
flecha(6.45, 10.3, 6.35, 10.3, "Sí", VERDE)   # decision -> derecha
flecha(3.55, 10.3, 3.65, 10.3, "No", "#DC2626")  # decision -> izquierda
# Punto de unión (merge) de las dos ramas
ax.add_patch(plt.Circle((5, 9.35), 0.16, facecolor="white",
             edgecolor="#475569", lw=1.6))
flecha(8.0, 9.82, 5.22, 9.45)      # derecha -> merge
flecha(2.0, 9.82, 4.78, 9.45)      # izquierda -> merge
flecha(5, 9.19, 5, 8.9)            # merge -> calcular
flecha(5, 7.92, 5, 7.4)            # merge -> restar
flecha(5, 6.42, 5, 5.9)            # restar -> indice
flecha(5, 4.92, 5, 4.4)            # indice -> turno
flecha(5, 3.42, 5, 3.0)           # turno -> salida
flecha(5, 2.0, 5, 1.65)            # salida -> fin

plt.tight_layout()
plt.savefig("/app/figura_3_2.png", bbox_inches="tight", facecolor="white")
print("OK -> /app/figura_3_2.png")
