"""Actualiza los números de página de los índices (contenido, figuras, tablas)
según el PDF renderizado del manual. Uso: python manual_actualizar_indices.py in.docx in.pdf out.docx"""
import sys, re
import pymupdf
from docx import Document
from docx.oxml.ns import qn

DOCX, PDF, OUT = sys.argv[1:4]
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
pdf = pymupdf.open(PDF)
paginas = [norm(p.get_text()) for p in pdf]
INICIO = 6  # saltar portada e índices

d = Document(DOCX)
cambios = 0
for p in d.paragraphs:
    if not p.style.name.lower().startswith('toc'):
        continue
    titulo = norm(p.text.rsplit('\t', 1)[0])
    pag = next((i + 1 for i in range(INICIO, len(paginas)) if titulo in paginas[i]), None)
    if pag is None:
        print('NO ENCONTRADO:', titulo)
        continue
    ts = [t for t in p._p.iter(qn('w:t')) if t.text and t.text.strip().isdigit()]
    if ts and ts[-1].text.strip() != str(pag):
        ts[-1].text = str(pag)
        cambios += 1
d.save(OUT)
print('Entradas actualizadas:', cambios)
