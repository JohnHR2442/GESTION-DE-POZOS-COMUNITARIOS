# -*- coding: utf-8 -*-
"""Diagrama de flujo del calculo del turno del dia, con flechas limpias (estilo estandar)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Polygon, Circle
from matplotlib.patches import FancyArrowPatch

# Colores
AZUL_BORDE = '#1F8FD6'
AZUL_FILL = '#E8F4FC'
AZUL_OSC = '#1F6FB0'
AMAR_BORDE = '#E6B800'
AMAR_FILL = '#FFF6D6'
VERDE_BORDE = '#5FB85F'
VERDE_FILL = '#E6F6E6'
TXT = '#1A1A1A'

fig, ax = plt.subplots(figsize=(7.2, 11.2))
ax.set_xlim(0, 100)
ax.set_ylim(0, 170)
ax.axis('off')

CX = 50  # eje central


def proc(xc, yc, w, h, text, fill=AZUL_FILL, border=AZUL_BORDE, fs=9.5):
    box = FancyBboxPatch((xc - w/2, yc - h/2), w, h,
                         boxstyle="round,pad=0.02,rounding_size=1.5",
                         linewidth=1.6, edgecolor=border, facecolor=fill)
    ax.add_patch(box)
    ax.text(xc, yc, text, ha='center', va='center', fontsize=fs, color=TXT, wrap=True)


def terminal(xc, yc, w, h, text):
    e = Ellipse((xc, yc), w, h, linewidth=1.6, edgecolor=AZUL_OSC, facecolor=AZUL_OSC)
    ax.add_patch(e)
    ax.text(xc, yc, text, ha='center', va='center', fontsize=10, color='white', fontweight='bold')


def decision(xc, yc, w, h, text):
    pts = [(xc, yc + h/2), (xc + w/2, yc), (xc, yc - h/2), (xc - w/2, yc)]
    d = Polygon(pts, closed=True, linewidth=1.6, edgecolor=AMAR_BORDE, facecolor=AMAR_FILL)
    ax.add_patch(d)
    ax.text(xc, yc, text, ha='center', va='center', fontsize=9, color=TXT)


def iotext(xc, yc, w, h, text, fs=9.5):
    sk = 5
    pts = [(xc - w/2 + sk, yc + h/2), (xc + w/2 + sk, yc + h/2),
           (xc + w/2 - sk, yc - h/2), (xc - w/2 - sk, yc - h/2)]
    p = Polygon(pts, closed=True, linewidth=1.6, edgecolor=VERDE_BORDE, facecolor=VERDE_FILL)
    ax.add_patch(p)
    ax.text(xc, yc, text, ha='center', va='center', fontsize=9.5, color=TXT)


def arrow(x1, y1, x2, y2):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=16,
                        linewidth=1.5, color='#444444', shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def elbow(x1, y1, x2, y2, first='v'):
    # conector en L con cabeza al final
    if first == 'v':
        mid = (x1, y2)
    else:
        mid = (x2, y1)
    ax.plot([x1, mid[0]], [y1, mid[1]], color='#444444', linewidth=1.5, solid_capstyle='round')
    arrow(mid[0], mid[1], x2, y2)


# ---- Nodos (de arriba a abajo) ----
terminal(CX, 162, 24, 9, 'INICIO')
proc(CX, 148, 44, 11, 'Obtener fecha y hora\nlocal (UTC-6)')
decision(CX, 130, 34, 18, '¿Hora actual\n≥ 18:00?')

# cajas laterales (debajo y a los lados, estilo del ejemplo)
LX, RX = 20, 80
LBY = 108
proc(LX, LBY, 30, 12, 'fecha_efectiva =\nfecha actual', fs=9)
proc(RX, LBY, 30, 12, 'fecha_efectiva =\nfecha + 1 día', fs=9)

proc(CX, 90, 46, 12, 'Calcular días transcurridos\n(fecha_efectiva − inicio_rotación)', fs=8.7)
proc(CX, 73, 46, 12, 'Restar festivos y días sin\nservicio → días válidos', fs=9)
proc(CX, 56, 46, 12, 'índice = días_válidos\nmód total_de_socios', fs=9)
proc(CX, 39, 46, 11, 'turno = lista_socios[índice]', fs=9)
iotext(CX, 24, 46, 11, 'Mostrar el turno del día', fs=9)
terminal(CX, 9, 24, 9, 'FIN')

# ---- Flechas ----
arrow(CX, 157.5, CX, 153.5)          # inicio -> obtener
arrow(CX, 142.5, CX, 139)            # obtener -> decision

# decision -> cajas laterales (L-shape) con etiquetas
# No (izquierda)
ax.plot([CX - 17, LX], [130, 130], color='#444444', linewidth=1.5)
arrow(LX, 130, LX, 114)
ax.text(CX - 19, 133, 'No', ha='center', color='#C0392B', fontsize=9.5, fontweight='bold')
# Si (derecha)
ax.plot([CX + 17, RX], [130, 130], color='#444444', linewidth=1.5)
arrow(RX, 130, RX, 114)
ax.text(CX + 19, 133, 'Sí', ha='center', color='#1E7D32', fontsize=9.5, fontweight='bold')

# cajas laterales -> se reunen y bajan a "Calcular dias"
MERGE_Y = 99
ax.plot([LX, LX], [102, MERGE_Y], color='#444444', linewidth=1.5)
ax.plot([RX, RX], [102, MERGE_Y], color='#444444', linewidth=1.5)
ax.plot([LX, RX], [MERGE_Y, MERGE_Y], color='#444444', linewidth=1.5)
arrow(CX, MERGE_Y, CX, 96)           # merge -> Calcular dias

# cadena vertical central
arrow(CX, 84, CX, 79)                # calcular -> restar
arrow(CX, 67, CX, 62)                # restar -> indice
arrow(CX, 50, CX, 44.5)              # indice -> turno
arrow(CX, 33.5, CX, 29.5)            # turno -> mostrar
arrow(CX, 18.5, CX, 13.5)            # mostrar -> fin

plt.tight_layout()
plt.savefig('/app/figura_flujo_turno.png', dpi=160, bbox_inches='tight', facecolor='white')
plt.close()
print('OK figura_flujo_turno.png')
