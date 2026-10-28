"""Coloca la Figura 14 (grafo de competencias) en una hoja horizontal propia.
Uso: python grafo_horizontal.py tesis.docx salida.docx"""
import sys, copy
from docx import Document
from docx.oxml.ns import qn

SRC, DST = sys.argv[1:3]
d = Document(SRC)
ps = d.paragraphs
i_cap = next(i for i, p in enumerate(ps) if p.style.name == 'Cap_Figura' and p.text.startswith('Figura 14. Grafo'))
p_img, p_cap, p_fuente = ps[i_cap - 1], ps[i_cap], ps[i_cap + 1]
p_antes = ps[i_cap - 2]
assert 'graphic' in p_img._p.xml and p_fuente.text.startswith('Fuente')

base = d.element.body.find(qn('w:sectPr'))  # sección vertical actual (mismo encabezado y pie)

# 1) Cerrar la sección vertical antes del grafo
vertical = copy.deepcopy(base)
p_antes._p.get_or_add_pPr().append(vertical)

# 2) La hoja del grafo es horizontal
horizontal = copy.deepcopy(base)
pg = horizontal.find(qn('w:pgSz'))
pg.set(qn('w:w'), '15840'); pg.set(qn('w:h'), '12240'); pg.set(qn('w:orient'), 'landscape')
p_fuente._p.get_or_add_pPr().append(horizontal)

# 3) Agrandar el grafo al ancho de la hoja horizontal (22 cm)
ext = p_img._p.find('.//' + qn('wp:extent'))
cx, cy = int(ext.get('cx')), int(ext.get('cy'))
nuevo_cx = int(22 * 360000)
nuevo_cy = int(cy * nuevo_cx / cx)
for e in p_img._p.iter(qn('wp:extent'), qn('a:ext')):
    e.set('cx', str(nuevo_cx)); e.set('cy', str(nuevo_cy))

d.save(DST)
print('OK', DST)
