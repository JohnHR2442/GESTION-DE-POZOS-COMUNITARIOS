"""Compacta el manual para que quepan dos pasos (con su figura) por hoja."""
import sys
from docx import Document
from docx.shared import Pt, Emu
from docx.oxml.ns import qn

SRC, DST = sys.argv[1], sys.argv[2]
ALTO = Emu(int(6.3 * 360000))  # 7 cm de alto por captura

d = Document(SRC)
body = d.element.body

# 1) Reducir capturas a 7 cm de alto manteniendo proporción
for sh in d.inline_shapes:
    ratio = sh.width / sh.height
    sh.height = ALTO
    sh.width = Emu(int(ALTO * ratio))

# 2) Mantener imagen con su pie y ajustar espacios
for tbl in body.iter(qn('w:tbl')):
    if 'graphic' not in tbl.xml or len(tbl.findall(qn('w:tr'))) != 2:
        continue
    first_p = tbl.find(qn('w:tr')).find('.//' + qn('w:p'))
    pPr = first_p.get_or_add_pPr()
    if pPr.find(qn('w:keepNext')) is None:
        pPr.insert(0, pPr.makeelement(qn('w:keepNext'), {}))

paras = d.paragraphs
for i, p in enumerate(paras):
    t = p.text.strip()
    if t.startswith('Paso '):
        pf = p.paragraph_format
        pf.space_before = Pt(4)
        pf.space_after = Pt(4)
        pf.line_spacing = 1.15
    elif t == '' and 'graphic' not in p._p.xml and 'w:br' not in p._p.xml:
        prev = p._p.getprevious()
        # Espaciador después de una figura: hacerlo mínimo
        if prev is not None and prev.tag == qn('w:tbl') and 'graphic' in prev.xml:
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = Pt(6)
        # Eliminar párrafos vacíos duplicados dentro de las secciones de pasos
        elif prev is not None and prev.tag == qn('w:p') and i > 105:
            from docx.text.paragraph import Paragraph
            pp = Paragraph(prev, p._parent)
            if pp.text.strip() == '' and 'w:br' not in prev.xml and 'graphic' not in prev.xml:
                p._p.getparent().remove(p._p)

d.save(DST)
print('OK', DST)
