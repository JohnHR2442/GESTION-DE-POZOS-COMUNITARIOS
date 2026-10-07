# -*- coding: utf-8 -*-
"""Reemplaza la imagen del diagrama de flujo (image5) en el docx y ajusta su tamano."""
import docx
from docx.oxml.ns import qn
from PIL import Image

DOCX = '/app/Tesis_con_indices.docx'
NEW = '/app/figura_flujo_turno.png'

d = docx.Document(DOCX)
rels = d.part.rels

# dimensiones de la nueva imagen
im = Image.open(NEW)
nw, nh = im.size
ratio = nh / nw
newbytes = open(NEW, 'rb').read()

# localizar el drawing de image5 y su rId
target_rid = None
for rid, rel in rels.items():
    if rel.reltype.endswith('/image') and rel.target_ref.split('/')[-1].startswith('image5.'):
        target_rid = rid
        break
print('rId image5 =', target_rid)

# reemplazar blob de la parte de imagen
part = rels[target_rid].target_part
part._blob = newbytes
print('blob reemplazado, nuevo tamano bytes =', len(part._blob))

# ajustar extent del drawing que referencia ese rId
found = False
for p in d.paragraphs:
    blips = p._p.findall('.//' + qn('a:blip'))
    for blip in blips:
        if blip.get(qn('r:embed')) == target_rid:
            drawing = p._p.find('.//' + qn('w:drawing'))
            extent = drawing.find('.//' + qn('wp:extent'))
            cx = int(extent.get('cx'))
            new_cy = int(cx * ratio)
            extent.set('cy', str(new_cy))
            aext = drawing.find('.//' + qn('a:ext'))
            if aext is not None:
                aext.set('cx', str(cx)); aext.set('cy', str(new_cy))
            print(f'extent ajustado: cx={cx} cy_old-> cy={new_cy} (ratio={ratio:.3f})')
            found = True
print('drawing actualizado:', found)

d.save(DOCX)
print('Guardado', DOCX)
