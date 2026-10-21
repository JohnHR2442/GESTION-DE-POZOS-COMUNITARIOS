import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import textwrap

plt.rcParams["font.family"] = "Liberation Sans"

C = {
    "sel": ("#1E8E3E", "white"),     # Seleccionada
    "dir": ("#1A3D99", "white"),     # Aporte directo
    "ind": ("#9CC3F0", "black"),     # Aporte indirecto
    "esp": ("#F6C9AE", "black"),     # Especialidad
    "pdir": ("#F59B1E", "black"),    # Competencia previa directa
    "pind": ("#FFF59D", "black"),    # Competencia previa indirecta
    None: ("white", "#333333"),
}

plan = {
    1: [("Cálculo Diferencial", None), ("Fundamentos de Programación", "pdir"), ("Taller de Ética", "pind"),
        ("Matemáticas Discretas", "dir"), ("Taller de Administración", "pind"), ("Fundamentos de Investigación", "pind")],
    2: [("Cálculo Integral", None), ("Programación Orientada a Objetos", "pdir"), ("Contabilidad Financiera", "pind"),
        ("Química", None), ("Álgebra Lineal", None), ("Probabilidad y Estadística", "ind")],
    3: [("Cálculo Vectorial", None), ("Estructura de Datos", "pdir"), ("Tópicos Avanzados de Programación", "sel"),
        ("Cultura Empresarial", "pind"), ("Investigación de Operaciones", None), ("Física General", None),
        ("Desarrollo Sustentable", "pind")],
    4: [("Lenguajes y Autómatas I", None), ("Ecuaciones Diferenciales", None), ("Métodos Numéricos", None),
        ("Fundamentos de Base de Datos", "dir"), ("Sistemas Operativos", "ind"),
        ("Principios Eléctricos y Aplicaciones Digitales", None), ("Simulación", None)],
    5: [("Lenguajes y Autómatas II", None), ("Graficación", None), ("Fundamentos de Telecomunicaciones", None),
        ("Taller de Base de Datos", "sel"), ("Taller de Sistemas Operativos", None), ("Arquitectura de Computadoras", None),
        ("Fundamentos de Ingeniería de Software", "dir")],
    6: [("Programación Lógica y Funcional", None), ("Taller de Investigación I", "ind"), ("Redes de Computadoras", "dir"),
        ("Administración de Bases de Datos", "dir"), ("Tarjetas para Sistemas Autómatas", None),
        ("Lenguajes de Interfaz", None), ("Ingeniería de Software", "sel")],
    7: [("Inteligencia Artificial", None), ("Taller de Investigación II", "ind"),
        ("Conmutación y Enrutamiento de Redes de Datos", None), ("Programación Web", "sel"),
        ("Arquitecturas Reconfigurables", "esp"), ("Gestión de Proyectos de Software", "dir")],
    8: [("Programación de Robots", "esp"), ("Sistemas Programables", None), ("Administración de Redes", "ind"),
        ("Redes Neuronales Artificiales", "esp"), ("Seguridad en Redes", "esp"),
        ("Programación en Back y Front End", "sel")],
    9: [("Residencia Profesional", "sel")],
}

W, H, GX, GY = 1.0, 0.62, 0.22, 0.2
fig, ax = plt.subplots(figsize=(16, 9.6), dpi=220)
ax.set_xlim(-0.1, 9 * (W + GX))
ax.set_ylim(-2.2, 7 * (H + GY) + 0.7)
ax.axis("off")
top = 7 * (H + GY)

for s, materias in plan.items():
    x = (s - 1) * (W + GX)
    ax.add_patch(Rectangle((x, top + 0.12), W, 0.3, fc="white", ec="black", lw=1.6))
    ax.text(x + W / 2, top + 0.27, f"{s}", ha="center", va="center", fontsize=10, fontweight="bold")
    for i, (nom, cat) in enumerate(materias):
        y = top - (i + 1) * (H + GY) + GY
        fc, tc = C[cat]
        ax.add_patch(Rectangle((x, y), W, H, fc=fc, ec="#555555", lw=1.0))
        ax.text(x + W / 2, y + H / 2, "\n".join(textwrap.wrap(nom.upper(), 15)), ha="center", va="center",
                fontsize=6.4, color=tc, fontweight="bold" if cat else "normal", linespacing=1.15)

ax.text(4.5 * (W + GX) - GX / 2, top + 0.62, "Semestre", ha="center", fontsize=11, fontweight="bold")

leyenda = [("sel", "Seleccionada (aplicada directamente)"), ("dir", "Aporte directo"),
           ("pdir", "Competencia previa directa"), ("esp", "Especialidad"),
           ("ind", "Aporte indirecto"), ("pind", "Competencia previa indirecta")]
for k, (cat, txt) in enumerate(leyenda):
    col, fila = k % 3, k // 3
    x = 0.4 + col * 3.6
    y = -0.85 - fila * 0.62
    ax.add_patch(Rectangle((x, y), 0.75, 0.38, fc=C[cat][0], ec="#333333", lw=1))
    ax.text(x + 0.9, y + 0.19, txt, va="center", fontsize=10.5)

plt.savefig("/app/grafo_competencias.png", bbox_inches="tight", facecolor="white")
print("ok")
