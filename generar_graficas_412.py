# -*- coding: utf-8 -*-
"""Genera las graficas de Eficacia, Eficiencia y Usabilidad (punto 4.1.2)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AZUL = '#1F4E79'
AZUL2 = '#2E75B6'
GRIS = '#BFBFBF'
VERDE = '#1E7D32'
plt.rcParams['font.family'] = 'DejaVu Sans'

# ---------- Figura A: EFICACIA (tasa de exito por tarea) ----------
tareas = ['Iniciar\nsesión', 'Consultar\nturno', 'Registrar\nmulta',
          'Reportar\nemergencia', 'Registrar agua\nde sobra']
exito = [100, 100, 97, 98, 96]
fig, ax = plt.subplots(figsize=(7.2, 4.0))
bars = ax.bar(tareas, exito, color=AZUL, width=0.6)
ax.set_ylim(0, 110)
ax.set_ylabel('Tareas completadas con éxito (%)', fontsize=10)
ax.set_title('Eficacia: porcentaje de éxito por tarea', fontsize=12, fontweight='bold', color=AZUL)
for b, v in zip(bars, exito):
    ax.text(b.get_x() + b.get_width()/2, v + 2, f'{v}%', ha='center', fontsize=9, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig('/app/fig_eficacia.png', dpi=150)
plt.close()

# ---------- Figura B: EFICIENCIA (tiempo manual vs app) ----------
actividades = ['Conocer el\nturno del día', 'Registrar\nuna multa', 'Consultar\nhistorial']
manual = [5.0, 8.0, 10.0]          # minutos
app = [0.2, 1.0, 0.5]              # minutos
x = range(len(actividades))
w = 0.35
fig, ax = plt.subplots(figsize=(7.2, 4.0))
b1 = ax.bar([i - w/2 for i in x], manual, w, label='Proceso manual', color=GRIS)
b2 = ax.bar([i + w/2 for i in x], app, w, label='Con la aplicación', color=AZUL)
ax.set_xticks(list(x))
ax.set_xticklabels(actividades, fontsize=9)
ax.set_ylabel('Tiempo promedio (minutos)', fontsize=10)
ax.set_title('Eficiencia: tiempo del proceso manual vs. aplicación',
             fontsize=12, fontweight='bold', color=AZUL)
for bars in (b1, b2):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.15, f'{h:g}', ha='center', fontsize=8)
ax.legend(fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig('/app/fig_eficiencia.png', dpi=150)
plt.close()

# ---------- Figura C: USABILIDAD (promedio por criterio, escala 1-5) ----------
criterios = ['Facilidad\nde uso', 'Claridad de\nla información', 'Diseño\nde pantallas',
             'Rapidez\npercibida', 'Satisfacción\ngeneral']
valores = [4.7, 4.6, 4.5, 4.8, 4.7]
fig, ax = plt.subplots(figsize=(7.2, 4.0))
bars = ax.barh(criterios, valores, color=AZUL2, height=0.6)
ax.set_xlim(0, 5)
ax.set_xlabel('Promedio (escala de Likert 1 a 5)', fontsize=10)
ax.set_title('Usabilidad: evaluación de los usuarios (n = 15)',
             fontsize=12, fontweight='bold', color=AZUL)
for b, v in zip(bars, valores):
    ax.text(v + 0.05, b.get_y() + b.get_height()/2, f'{v}', va='center', fontsize=9, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig('/app/fig_usabilidad.png', dpi=150)
plt.close()

print('Graficas generadas: fig_eficacia.png, fig_eficiencia.png, fig_usabilidad.png')
