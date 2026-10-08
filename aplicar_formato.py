# -*- coding: utf-8 -*-
"""
Aplica el formato del instituto a Correccion_Tesis_Prof.docx:
 - Margenes 2.5/2.5/3/2.5
 - Cuerpo: Arial 11, justificado, interlineado 1.5, espacio despues 1 linea
 - Titulos de figura/tabla: Arial 9, SIN cursiva, centrados
 - Encabezado: nombre del tema (centrado). Pie: institucion (izq, Arial 9) + No. pagina (der, Arial 10)
 - Primera pagina (portada) sin encabezado/pie
 - NO toca: portada, entradas de indice (toc), celdas de tabla
"""
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = '/app/Correccion_Tesis_Prof.docx'
OUT = '/app/Tesis_Formateada.docx'
TEMA = 'SISTEMA INTEGRAL DE GESTIÓN DE POZOS COMUNITARIOS'
INSTITUCION = 'Instituto Tecnológico Superior de Tepeaca'

d = docx.Document(SRC)

# -------- 1) Margenes --------
for s in d.sections:
    s.top_margin = Cm(2.5)
    s.bottom_margin = Cm(2.5)
    s.left_margin = Cm(3)
    s.right_margin = Cm(2.5)

# -------- 2) Donde termina la portada --------
# La portada va hasta el parrafo que contiene "TEPEACA DE NEGRETE" (fecha de portada)
cover_end = 0
for i, p in enumerate(d.paragraphs):
    if 'TEPEACA DE NEGRETE' in p.text.upper():
        cover_end = i
        break
print('cover_end idx =', cover_end)

HEADING_STYLES = {'Heading 1', 'Heading 2', 'Heading 3', 'Título1', 'Subtitle', 'Title'}


def set_runs(p, name='Arial', size=None, italic=None):
    for r in p.runs:
        r.font.name = name
        # fijar tambien east asian / cs
        rpr = r._r.get_or_add_rPr()
        rfonts = rpr.find(qn('w:rFonts'))
        if rfonts is None:
            rfonts = OxmlElement('w:rFonts'); rpr.insert(0, rfonts)
        for a in ('w:ascii', 'w:hAnsi', 'w:cs'):
            rfonts.set(qn(a), name)
        if size is not None:
            r.font.size = Pt(size)
        if italic is not None:
            r.font.italic = italic


for i, p in enumerate(d.paragraphs):
    if i <= cover_end:
        continue  # no tocar portada
    sty = p.style.name
    if sty.startswith('toc'):
        continue  # no tocar indice general
    if sty in ('Cap_Figura', 'Cap_Tabla'):
        # titulo de figura/tabla: Arial 9, sin cursiva, centrado
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(3)
        pf.space_after = Pt(6)
        set_runs(p, 'Arial', size=9, italic=False)
        continue
    if sty in HEADING_STYLES:
        # titulos: fuente Arial, se conserva tamano/negrita; dos lineas despues
        set_runs(p, 'Arial')
        pf = p.paragraph_format
        pf.space_before = Pt(18)
        pf.space_after = Pt(18)
        continue
    # ---- cuerpo (Normal, List Paragraph, List Bullet, Default) ----
    txt = p.text.strip()
    if not txt:
        continue
    if sty in ('List Bullet', 'List Paragraph'):
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(12)   # una linea
    pf.space_before = Pt(0)
    set_runs(p, 'Arial', size=11)  # conserva negrita/cursiva existentes

# -------- 3) Encabezado y pie --------
sec = d.sections[0]
sec.different_first_page_header_footer = True  # portada sin encabezado/pie

# encabezado (paginas != portada)
hdr = sec.header
hdr.is_linked_to_previous = False
hp = hdr.paragraphs[0]
hp.text = ''
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = hp.add_run(TEMA)
r.font.name = 'Arial'; r.font.size = Pt(10)
rpr = r._r.get_or_add_rPr(); rf = OxmlElement('w:rFonts')
for a in ('w:ascii', 'w:hAnsi', 'w:cs'): rf.set(qn(a), 'Arial')
rpr.insert(0, rf)

# pie (institucion izq Arial9 + No pagina der Arial10)
ftr = sec.footer
ftr.is_linked_to_previous = False
fp = ftr.paragraphs[0]
fp.text = ''
# tab derecho al ancho de texto
page_w = sec.page_width
txt_w = page_w - sec.left_margin - sec.right_margin
fp.paragraph_format.tab_stops.add_tab_stop(txt_w, WD_TAB_ALIGNMENT.RIGHT)
# institucion
r1 = fp.add_run(INSTITUCION)
r1.font.name = 'Arial'; r1.font.size = Pt(9)
# tab
fp.add_run('\t')
# campo PAGE
r2 = fp.add_run()
r2.font.name = 'Arial'; r2.font.size = Pt(10)
fld1 = OxmlElement('w:fldChar'); fld1.set(qn('w:fldCharType'), 'begin')
instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = ' PAGE '
fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'), 'end')
r2._r.append(fld1); r2._r.append(instr); r2._r.append(fld2)

# primera pagina: encabezado y pie vacios (portada limpia)
fh = sec.first_page_header; fh.is_linked_to_previous = False
fh.paragraphs[0].text = ''
ff = sec.first_page_footer; ff.is_linked_to_previous = False
ff.paragraphs[0].text = ''

# -------- 4) actualizar campos al abrir --------
settings = d.settings.element
if settings.find(qn('w:updateFields')) is None:
    uf = OxmlElement('w:updateFields'); uf.set(qn('w:val'), 'true'); settings.append(uf)

d.save(OUT)
print('Guardado', OUT)
