# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AZUL = "#0284C7"
encabezados = ["Núm.", "Caso de prueba", "Entrada / acción",
               "Resultado esperado", "Resultado"]
filas = [
    ["CP-01", "Turno en día normal\nantes de las 18:00", "Consultar turno\na las 10:00",
     "Muestra el socio en\nturno de ese día", "Correcto"],
    ["CP-02", "Cambio de turno\na las 18:00", "Consultar turno\ndespués de las 18:00",
     "Muestra el socio del\ndía siguiente", "Correcto"],
    ["CP-03", "Día festivo", "Consultar turno\nen día festivo",
     "Recorre la rotación\nsin saltar socio", "Correcto"],
    ["CP-04", "Día sin servicio\n(turno caído)", "Marcar día sin servicio\ny consultar",
     "Recorre al socio\nsiguiente", "Correcto"],
    ["CP-05", "Inicio de sesión\nválido", "Correo y contraseña\ncorrectos",
     "Acceso concedido\nsegún el rol", "Correcto"],
    ["CP-06", "Inicio de sesión\ninválido", "Contraseña incorrecta",
     "Muestra mensaje\nde error", "Correcto"],
    ["CP-07", "Registro de multa", "El contador registra\nuna multa",
     "La multa se guarda y\nel socio la ve", "Correcto"],
    ["CP-08", "Aislamiento por pozo", "Socio consulta su\ninformación",
     "Solo ve datos de\nsu propio pozo", "Correcto"],
    ["CP-09", "Recuperación de\ncontraseña", "Solicitar recuperación\npor correo",
     "Llega un correo\ncon el código", "Correcto"],
]

fig, ax = plt.subplots(figsize=(13, 6.5), dpi=155)
ax.axis("off")

tabla = ax.table(cellText=filas, colLabels=encabezados,
                 cellLoc="left", loc="center",
                 colWidths=[0.09, 0.22, 0.24, 0.27, 0.12])
tabla.auto_set_font_size(False)
tabla.set_fontsize(9.5)
tabla.scale(1, 3.2)

for (r, c), cell in tabla.get_celld().items():
    cell.set_edgecolor("#94A3B8")
    cell.set_linewidth(0.8)
    if r == 0:
        cell.set_facecolor(AZUL)
        cell.set_text_props(color="white", fontweight="bold")
        cell.set_height(cell.get_height() * 0.8)
    else:
        cell.set_facecolor("#F1F5F9" if r % 2 == 0 else "white")
        if c == 4:
            cell.set_text_props(color="#15803D", fontweight="bold")
        if c == 0:
            cell.set_text_props(fontweight="bold", color="#0C4A6E")

plt.tight_layout()
plt.savefig("/app/tabla_4_1.png", bbox_inches="tight", facecolor="white")
print("OK -> /app/tabla_4_1.png")
