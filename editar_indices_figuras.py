# -*- coding: utf-8 -*-
"""
Edita correccion_Tesis.docx EN SITIO:
 - Titula las 12 figuras (Figura 1..12) en formato del instituto (abajo de la imagen).
 - Titula las 13 tablas (Tabla 1..13) con el nombre ARRIBA de la tabla.
 - Reconstruye el Indice de Figuras y el Indice de Tablas con campos automaticos (con pagina).
 - Actualiza las referencias en el texto (Figura 4.1/4.2/4.3 -> 10/11/12).
"""
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE

SRC = '/app/correccion_Tesis.docx'
OUT = '/app/Tesis_con_indices.docx'

d = docx.Document(SRC)
styles = d.styles

# ---------- 1) estilos de epigrafe ----------
def ensure_style(name):
    existing = {s.name: s for s in styles}
    if name in existing:
        return existing[name]
    st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    st.base_style = styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(10)
    st.font.italic = True
    st.font.bold = False
    return st

sfig = ensure_style('Cap_Figura')
stab = ensure_style('Cap_Tabla')
FIG_ID = sfig.style_id
TAB_ID = stab.style_id


def make_caption_p(text, style_id):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    ps = OxmlElement('w:pStyle'); ps.set(qn('w:val'), style_id); pPr.append(ps)
    jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'center'); pPr.append(jc)
    sp = OxmlElement('w:spacing'); sp.set(qn('w:before'), '60'); sp.set(qn('w:after'), '120'); pPr.append(sp)
    p.append(pPr)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts'); rf.set(qn('w:ascii'), 'Arial'); rf.set(qn('w:hAnsi'), 'Arial'); rPr.append(rf)
    it = OxmlElement('w:i'); rPr.append(it)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '20'); rPr.append(sz)
    r.append(rPr)
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text; r.append(t)
    p.append(r)
    return p


def set_para_text_style(p, text, style_id):
    # elimina runs y deja uno solo, aplica estilo de parrafo
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    run = p.add_run(text)
    run.font.name = 'Arial'; run.font.size = Pt(10); run.italic = True
    p.style = styles.get_by_id(style_id, WD_STYLE_TYPE.PARAGRAPH)
    # centrar
    pPr = p._p.get_or_add_pPr()
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc'); pPr.append(jc)
    jc.set(qn('w:val'), 'center')


# ---------- 2) FIGURAS ----------
from docx.oxml.ns import qn as _qn

def para_has_image(p):
    return bool(p._p.findall('.//' + _qn('a:blip')))

fig_names = {
    'image4': 'Figura 1. Diagrama de casos de uso del sistema.',
    'image5': 'Figura 2. Diagrama de flujo del cálculo del turno del día.',
    'image6': 'Figura 3. Fases de la metodología de desarrollo incremental.',
    'image7': 'Figura 4. Pantalla de inicio de sesión de la aplicación.',
    'image8': 'Figura 5. Pantalla de perfil del socio.',
    'image9': 'Figura 6. Pantalla de gestión de multas.',
    'image10': 'Figura 7. Pantalla de recorrido y registro de días sin servicio.',
    'image11': 'Figura 8. Pantalla principal del socio con el reporte de emergencias.',
    'image12': 'Figura 9. Pantalla de registro de agua de sobra.',
}
rels = d.part.rels

def image_name_of(p):
    blips = p._p.findall('.//' + _qn('a:blip'))
    if not blips:
        return None
    embed = blips[0].get(_qn('r:embed'))
    if embed in rels:
        return rels[embed].target_ref.split('/')[-1].split('.')[0]
    return None

paras = d.paragraphs
# a) caso de uso: el parrafo siguiente dice DIAGRAMA CASOS DE USO -> reemplazar
for i, p in enumerate(paras):
    nm = image_name_of(p)
    if nm == 'image4':
        # siguiente parrafo con texto
        nxt = paras[i + 1]
        set_para_text_style(nxt, fig_names['image4'], FIG_ID)
    elif nm in ('image5', 'image6', 'image7', 'image8', 'image9', 'image10', 'image11', 'image12'):
        cap = make_caption_p(fig_names[nm], FIG_ID)
        p._p.addnext(cap)

# b) las 3 graficas ya tienen caption "Figura 4.x ..." -> reescribir
chart_caps = {
    'Figura 4.1': 'Figura 10. Eficacia: porcentaje de éxito por tarea.',
    'Figura 4.2': 'Figura 11. Eficiencia: comparación del tiempo (proceso manual vs. aplicación).',
    'Figura 4.3': 'Figura 12. Usabilidad: evaluación promedio de los usuarios por criterio.',
}
for p in d.paragraphs:
    txt = p.text.strip()
    for k, v in chart_caps.items():
        if txt.startswith(k):
            set_para_text_style(p, v, FIG_ID)

# c) referencias en el texto Figura 4.x -> 10/11/12
ref_map = {'Figura 4.1': 'Figura 10', 'Figura 4.2': 'Figura 11', 'Figura 4.3': 'Figura 12'}
for p in d.paragraphs:
    full = p.text
    if any(k in full for k in ref_map) and not p.text.strip().startswith('Figura 1'):
        # solo parrafos de cuerpo (no captions ya reescritos)
        if p.style.name in ('Cap_Figura',):
            continue
        for r in p.runs:
            for k, v in ref_map.items():
                if k in r.text:
                    r.text = r.text.replace(k, v)

# ---------- 3) TABLAS ----------
tab_names = [
    'Tabla 1. Operacionalización de la variable independiente.',
    'Tabla 2. Operacionalización de la variable dependiente.',
    'Tabla 3. Distribución de la población por pozo comunitario.',
    'Tabla 4. Recursos materiales del proyecto.',
    'Tabla 5. Recursos de capital humano del proyecto.',
    'Tabla 6. Requerimientos funcionales del sistema.',
    'Tabla 7. Requerimientos no funcionales del sistema.',
    'Tabla 8. Modelado de la base de datos del sistema.',
    'Tabla 9. Resultados de las pruebas de requerimientos funcionales.',
    'Tabla 10. Resultados de las pruebas de requerimientos no funcionales.',
    'Tabla 11. Comparación de tiempos entre el proceso manual y la aplicación.',
    'Tabla 12. Calendario de mantenimiento preventivo.',
    'Tabla 13. Tiempos de respuesta del mantenimiento correctivo.',
]
tables = d.tables
assert len(tables) == 13, f"esperaba 13 tablas, hay {len(tables)}"
for tbl, name in zip(tables, tab_names):
    cap = make_caption_p(name, TAB_ID)
    tbl._tbl.addprevious(cap)

# borrar los viejos titulos/etiquetas de tabla
delete_texts = {
    'tabla de operacionalización de variables',
    'tabla 3.1 distribución de la población por pozo comunitario.',
    'recursos materiales',
    'recursos de capital humano',
    'tabla 3.2 requerimientos funcionales del sistema.',
    'tabla 3.3 requerimientos no funcionales del sistema.',
    'tabla 4.2 resultados de las pruebas de requerimientos funcionales.',
    'tabla 4.3 resultados de las pruebas de requerimientos no funcionales.',
    'tabla 4.1 comparación de tiempos entre el proceso manual y la aplicación.',
    'tabla 4.4 calendario de mantenimiento preventivo.',
    'tabla 4.5 tiempos de respuesta del mantenimiento correctivo.',
}
for p in list(d.paragraphs):
    if p.text.strip().lower() in delete_texts:
        p._p.getparent().remove(p._p)

# ---------- 4) INDICES AUTOMATICOS ----------
def make_toc_field_p(style_name):
    p = OxmlElement('w:p')
    for instr, placeholder in [(f' TOC \\h \\z \\t "{style_name},1" ',
                                'Haz clic derecho aquí y elige "Actualizar campo" para generar el índice.')]:
        r1 = OxmlElement('w:r'); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'begin'); r1.append(fc); p.append(r1)
        r2 = OxmlElement('w:r'); it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr; r2.append(it); p.append(r2)
        r3 = OxmlElement('w:r'); fc2 = OxmlElement('w:fldChar'); fc2.set(qn('w:fldCharType'), 'separate'); r3.append(fc2); p.append(r3)
        r4 = OxmlElement('w:r'); t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = placeholder; r4.append(t); p.append(r4)
        r5 = OxmlElement('w:r'); fc3 = OxmlElement('w:fldChar'); fc3.set(qn('w:fldCharType'), 'end'); r5.append(fc3); p.append(r5)
    return p

# Indice de figuras: reemplazar las 2 lineas placeholder "Figura 1/2. Nombre de la figura"
def replace_placeholders(label_startswith, style_name):
    targets = [p for p in d.paragraphs if p.text.strip().lower().startswith(label_startswith)]
    if not targets:
        print('NO encontre placeholders para', label_startswith)
        return
    first = targets[0]
    field_p = make_toc_field_p(style_name)
    first._p.addprevious(field_p)
    for p in targets:
        p._p.getparent().remove(p._p)

replace_placeholders('figura 1. nombre de la figura', 'Cap_Figura')
replace_placeholders('figura 2. nombre de la figura', 'Cap_Figura') if False else None
# borrar la 2a linea restante si quedo
for p in list(d.paragraphs):
    if p.text.strip().lower().startswith('figura 2. nombre de la figura'):
        p._p.getparent().remove(p._p)

replace_placeholders('tabla 1. nombre de la tabla', 'Cap_Tabla')
for p in list(d.paragraphs):
    if p.text.strip().lower().startswith('tabla 2. nombre de la tabla'):
        p._p.getparent().remove(p._p)

# ---------- 5) forzar actualizacion de campos al abrir ----------
settings = d.settings.element
if settings.find(qn('w:updateFields')) is None:
    uf = OxmlElement('w:updateFields'); uf.set(qn('w:val'), 'true')
    settings.append(uf)

d.save(OUT)
print('Guardado:', OUT)
