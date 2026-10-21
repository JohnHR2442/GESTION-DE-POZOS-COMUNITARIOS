import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Liberation Sans"

AZUL = "#1F3A5F"
AZUL_CLARO = "#DCE6F2"
VERDE = "#2E7D32"
VERDE_CLARO = "#E3F2E1"
GRIS = "#F2F2F2"

fig, ax = plt.subplots(figsize=(12, 9), dpi=200)
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis("off")

W, H = 3.0, 0.95


def caja(x, y, titulo, sub, fondo=AZUL_CLARO, borde=AZUL, w=W, estilo="-", grosor=1.6):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - H / 2), w, H,
                                boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fondo, ec=borde, lw=grosor, ls=estilo, zorder=3))
    ax.text(x, y + 0.14, titulo, ha="center", va="center", fontsize=10.5,
            fontweight="bold", color=borde, zorder=4)
    ax.text(x, y - 0.20, sub, ha="center", va="center", fontsize=8.8,
            color="#333333", zorder=4)


def linea(xs, ys, estilo="-"):
    ax.plot(xs, ys, color="#555555", lw=1.4, ls=estilo, zorder=1)


# Nivel 1
caja(6, 8.1, "Asamblea General de Ejidatarios", "Máxima autoridad deliberativa", fondo=AZUL, borde=AZUL)
ax.texts[-2].set_color("white"); ax.texts[-1].set_color("white")

# Nivel 2
caja(6, 6.6, "Comisariado Ejidal", "Presidente(a) del Comisariado")
caja(10.2, 6.6, "Consejo de Vigilancia", "Supervisión y auditoría interna", fondo=GRIS, borde="#555555", w=2.9)

# Nivel 3
caja(3.6, 5.0, "Secretaría", "Secretario(a) del Comisariado")
caja(8.4, 5.0, "Tesorería", "Tesorero(a) del Comisariado")

# Nivel 4
caja(3.6, 3.4, "Subcomité Técnico de Aguas", "y Pozos Hidráulicos · Encargado Operativo", w=3.5)

# Nivel 5
caja(1.9, 1.6, "Auxiliar Técnico", "Capturista de datos")
caja(5.6, 1.6, "Desarrollador del Sistema", "Egresado de Ing. en Sistemas Computacionales",
     fondo=VERDE_CLARO, borde=VERDE, w=3.4, grosor=2.6)

# Conexiones jerárquicas
linea([6, 6], [8.1 - H / 2, 6.6 + H / 2])
linea([6, 6], [6.6 - H / 2, 5.85])
linea([3.6, 8.4], [5.85, 5.85])
linea([3.6, 3.6], [5.85, 5.0 + H / 2])
linea([8.4, 8.4], [5.85, 5.0 + H / 2])
linea([3.6, 3.6], [5.0 - H / 2, 3.4 + H / 2])
linea([3.6, 3.6], [3.4 - H / 2, 2.4])
linea([1.9, 5.6], [2.4, 2.4])
linea([1.9, 1.9], [2.4, 1.6 + H / 2])
linea([5.6, 5.6], [2.4, 1.6 + H / 2])

# Consejo de Vigilancia (dependencia directa de la Asamblea, línea punteada de supervisión)
linea([10.2, 10.2], [7.35, 6.6 + H / 2])
linea([6, 10.2], [7.35, 7.35])

# Coordinación Tesorería - Subcomité (validación de aportaciones)
linea([8.4, 8.4], [5.0 - H / 2, 3.4])
linea([3.6 + 3.5 / 2, 8.4], [3.4, 3.4], estilo="--")

# Pozos atendidos
ax.text(9.6, 2.0, "Pozos atendidos por el Subcomité:", fontsize=9, fontweight="bold", color=AZUL, ha="center")
for i, p in enumerate(["Pozo San Isidro", "Pozo Cárdenas", "Pozo Zapata"]):
    ax.text(8.75, 1.6 - i * 0.33, "•  " + p, fontsize=9, color="#333333", ha="left")

# Simbología
ax.plot([0.4, 0.9], [0.35, 0.35], color="#555555", lw=1.4)
ax.text(1.0, 0.35, "Línea de mando", fontsize=8, va="center")
ax.plot([2.8, 3.3], [0.35, 0.35], color="#555555", lw=1.4, ls="--")
ax.text(3.4, 0.35, "Coordinación / supervisión", fontsize=8, va="center")
ax.add_patch(FancyBboxPatch((6.0, 0.22), 0.5, 0.26, boxstyle="round,pad=0.01",
                            fc=VERDE_CLARO, ec=VERDE, lw=2))
ax.text(6.65, 0.35, "Puesto desempeñado por el autor del proyecto", fontsize=8, va="center")

plt.savefig("/app/organigrama_comisariado.png", bbox_inches="tight", facecolor="white")
print("ok")
