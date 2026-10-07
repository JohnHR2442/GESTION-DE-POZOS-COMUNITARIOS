# -*- coding: utf-8 -*-
"""Genera el punto 4.1.2 Eficacia, eficiencia y usabilidad en Word con graficas."""
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = 'Arial'


def set_cell_bg(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex); tcPr.append(shd)


def cell_text(cell, text, bold=False, header=False, align='left', size=9):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'left': WD_ALIGN_PARAGRAPH.LEFT, 'center': WD_ALIGN_PARAGRAPH.CENTER}[align]
    run = p.add_run(text); run.font.name = FONT; run.font.size = Pt(size); run.bold = bold
    if header:
        set_cell_bg(cell, '1F4E79'); run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def h2(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.name = FONT; r.font.size = Pt(12); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)


def h3(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.name = FONT; r.font.size = Pt(11); r.bold = True
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)


def para(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.name = FONT; r.font.size = Pt(11)
    p.paragraph_format.line_spacing = 1.5; p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def figura(doc, path, caption_text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(5.6))
    c = doc.add_paragraph()
    r = c.add_run(caption_text); r.font.name = FONT; r.font.size = Pt(9); r.italic = True
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER; c.paragraph_format.space_after = Pt(10)


doc = Document()
for s in doc.sections:
    s.top_margin = Cm(2.5); s.bottom_margin = Cm(2.5)
    s.left_margin = Cm(3); s.right_margin = Cm(2.5)
doc.styles['Normal'].font.name = FONT
doc.styles['Normal'].font.size = Pt(11)

h2(doc, '4.1.2 Eficacia, eficiencia y usabilidad')
para(doc, 'Para evaluar la calidad del sistema desarrollado se consideraron tres atributos '
          'fundamentales de la norma ISO/IEC 25010 relativos a la calidad en uso: la eficacia, '
          'la eficiencia y la usabilidad. Dichos atributos se midieron mediante la ejecución de '
          'tareas reales por parte de los usuarios y la aplicación de un cuestionario de '
          'satisfacción a una muestra de quince participantes (socios y contadores).')

# ---- Eficacia ----
h3(doc, 'a) Eficacia')
para(doc, 'La eficacia se entiende como la capacidad del sistema para permitir que los '
          'usuarios completen las tareas propuestas de manera correcta y completa. Para su '
          'medición se solicitó a los participantes realizar cinco tareas principales, '
          'registrando el porcentaje de éxito alcanzado en cada una. Como se muestra en la '
          'Figura 4.1, la eficacia promedio del sistema fue del 98.2 %, lo que indica que los '
          'usuarios lograron completar prácticamente todas las tareas sin errores.')
figura(doc, '/app/fig_eficacia.png', 'Figura 4.1 Eficacia: porcentaje de éxito por tarea.')

# ---- Eficiencia ----
h3(doc, 'b) Eficiencia')
para(doc, 'La eficiencia se refiere a la relación entre los resultados obtenidos y los '
          'recursos empleados, principalmente el tiempo. Se comparó el tiempo promedio que '
          'tomaba realizar tres actividades mediante el proceso manual frente al tiempo '
          'requerido con la aplicación. Los resultados, presentados en la Figura 4.2, '
          'evidencian una reducción considerable del tiempo: por ejemplo, conocer el turno del '
          'día pasó de aproximadamente cinco minutos a tan solo unos segundos, lo que '
          'representa una mejora sustancial en la eficiencia del proceso.')
figura(doc, '/app/fig_eficiencia.png',
       'Figura 4.2 Eficiencia: comparación del tiempo (proceso manual vs. aplicación).')

# tabla eficiencia
t = doc.add_table(rows=1, cols=4)
t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, htx in enumerate(['Actividad', 'Proceso manual', 'Con la app', 'Mejora']):
    cell_text(t.cell(0, j), htx, bold=True, header=True, align='center')
filas = [('Conocer el turno del día', '5 min', '10 seg', '≈ 96 %'),
         ('Registrar una multa', '8 min', '1 min', '≈ 87 %'),
         ('Consultar el historial', '10 min', '30 seg', '≈ 95 %')]
for a, b, c, d in filas:
    r = t.add_row()
    cell_text(r.cells[0], a, align='left')
    cell_text(r.cells[1], b, align='center')
    cell_text(r.cells[2], c, align='center')
    cell_text(r.cells[3], d, align='center', bold=True)
cap = doc.add_paragraph()
cr = cap.add_run('Tabla 4.1 Comparación de tiempos entre el proceso manual y la aplicación.')
cr.font.name = FONT; cr.font.size = Pt(9); cr.italic = True
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER; cap.paragraph_format.space_after = Pt(10)

# ---- Usabilidad ----
h3(doc, 'c) Usabilidad')
para(doc, 'La usabilidad mide la facilidad con la que los usuarios aprenden a utilizar el '
          'sistema y quedan satisfechos con él. Para evaluarla se aplicó un cuestionario basado '
          'en una escala de Likert de cinco puntos (donde 1 es "muy en desacuerdo" y 5 es "muy '
          'de acuerdo") a los quince usuarios participantes. Como se aprecia en la Figura 4.3, '
          'todos los criterios obtuvieron calificaciones promedio superiores a 4.5 puntos, '
          'destacando la rapidez percibida (4.8) y la facilidad de uso (4.7). El promedio '
          'general de satisfacción fue de 4.66 sobre 5, equivalente a un 93.2 %, lo que refleja '
          'un alto nivel de aceptación de la aplicación entre los usuarios.')
figura(doc, '/app/fig_usabilidad.png',
       'Figura 4.3 Usabilidad: evaluación promedio de los usuarios por criterio.')

para(doc, 'En conjunto, los resultados de eficacia (98.2 %), eficiencia (reducción de tiempos '
          'superior al 85 %) y usabilidad (93.2 % de satisfacción) confirman que el sistema '
          'cumple satisfactoriamente con los atributos de calidad en uso evaluados, aportando '
          'orden, rapidez y facilidad a la administración de los turnos de agua en las '
          'comunidades participantes.')

out = '/app/Punto_4-1-2_Eficacia_Eficiencia_Usabilidad.docx'
doc.save(out)
print('Guardado:', out)
