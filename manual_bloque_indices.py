
# ======================= ESTILOS DE TÍTULOS E ÍNDICES =======================
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.text.paragraph import Paragraph


def estilo_cap(nombre):
    s = doc.styles.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = doc.styles["Caption"]
    s.font.name = "Arial"; s.font.size = Pt(9); s.font.italic = False; s.font.bold = False
    s.font.color.rgb = RGBColor(0, 0, 0)
    return s


cf, ct = estilo_cap("Cap_Figura"), estilo_cap("Cap_Tabla")
figs, tabs = [], []
for el in doc.element.body.iter(qn("w:p")):
    par = Paragraph(el, doc)
    t = par.text.strip()
    if par.style.name == "Caption" and t.startswith("Figura "):
        par.style = cf; figs.append(t)
    elif par.style.name == "Caption" and t.startswith("Tabla "):
        par.style = ct; tabs.append(t)

ind = doc.styles.add_style("Indice_Figuras_Tablas", WD_STYLE_TYPE.PARAGRAPH)
ind.base_style = doc.styles["Normal"]
ind.paragraph_format.line_spacing = 1.15
ind.paragraph_format.space_after = Pt(3)
ind.paragraph_format.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)


def r_fld(tipo):
    r = OxmlElement("w:r"); f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), tipo); r.append(f); return r


def r_txt(t, tab=False):
    r = OxmlElement("w:r")
    if tab:
        r.append(OxmlElement("w:tab"))
    x = OxmlElement("w:t"); x.set(qn("xml:space"), "preserve"); x.text = t; r.append(x); return r


def bloque_indice(titulo, entradas, estilo):
    br = OxmlElement("w:p"); rr = OxmlElement("w:r"); b = OxmlElement("w:br"); b.set(qn("w:type"), "page")
    rr.append(b); br.append(rr)
    tp = OxmlElement("w:p"); pPr = OxmlElement("w:pPr"); jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center")
    pPr.append(jc); tp.append(pPr)
    rt = r_txt(titulo); rPr = OxmlElement("w:rPr"); rPr.append(OxmlElement("w:b"))
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "28"); rPr.append(sz); rt.insert(0, rPr); tp.append(rt)
    els = [br, tp]
    for k, e in enumerate(entradas):
        p_ = OxmlElement("w:p"); pPr = OxmlElement("w:pPr"); ps_ = OxmlElement("w:pStyle")
        ps_.set(qn("w:val"), ind.style_id); pPr.append(ps_); p_.append(pPr)
        if k == 0:
            p_.append(r_fld("begin"))
            r = OxmlElement("w:r"); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
            it.text = f' TOC \\h \\z \\t "{estilo},1" '; r.append(it); p_.append(r)
            p_.append(r_fld("separate"))
        p_.append(r_txt(e)); p_.append(r_txt(str(PAGINAS.get(e, "")), tab=True))
        if k == len(entradas) - 1:
            p_.append(r_fld("end"))
        els.append(p_)
    return els


import json, sys
PAGINAS = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
pos = pt._p
for el in bloque_indice("ÍNDICE DE FIGURAS", figs, "Cap_Figura") + bloque_indice("ÍNDICE DE TABLAS", tabs, "Cap_Tabla"):
    pos.addnext(el); pos = el
json.dump({"figs": figs, "tabs": tabs}, open("/tmp/caps2.json", "w"), ensure_ascii=False)
