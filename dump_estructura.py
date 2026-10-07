# -*- coding: utf-8 -*-
import docx
from docx.oxml.ns import qn

d = docx.Document('/app/correccion_Tesis.docx')
body = d.element.body

# Walk the body in document order, printing paragraphs, tables, and images
tbl_count = 0
idx = 0
for child in body.iterchildren():
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        # paragraph
        p = None
        for para in d.paragraphs:
            if para._p is child:
                p = para
                break
        if p is None:
            continue
        text = p.text.strip()
        style = p.style.name if p.style else ''
        has_img = bool(child.findall('.//' + qn('w:drawing')))
        label = ''
        if has_img:
            label = ' [IMG]'
        if text or has_img:
            print(f"{idx:3d} | {style[:18]:18s} | {text[:90]}{label}")
        idx += 1
    elif tag == 'tbl':
        tbl_count += 1
        print(f"    >>> TABLA #{tbl_count}")
        idx += 1
