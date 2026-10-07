# -*- coding: utf-8 -*-
import docx
from docx.oxml.ns import qn

d = docx.Document('/app/correccion_Tesis.docx')
rels = d.part.rels
body = d.element.body

seq = 0
for child in body.iterchildren():
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        blips = child.findall('.//' + qn('a:blip'))
        if blips:
            # nearby text (this para + next para caption)
            txt = ''.join(n.text or '' for n in child.iter(qn('w:t')))
            for blip in blips:
                embed = blip.get(qn('r:embed'))
                target = rels[embed].target_ref if embed in rels else '??'
                seq += 1
                print(f"IMG#{seq}: {target.split('/')[-1]:14s} | paratext='{txt[:40]}'")
