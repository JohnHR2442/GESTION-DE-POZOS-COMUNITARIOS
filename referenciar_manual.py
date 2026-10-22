import copy
import json
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "/app/manual_v2.docx"
OUT = "/app/Manual_de_Usuario_Referenciado.docx"
paginas = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}

d = Document(SRC)
W = qn("w:p")
ps = lambda: [Paragraph(e, d) for e in d.element.body.iter(W)]


def estilo(nombre):
    if nombre in [s.name for s in d.styles]:
        return d.styles[nombre]
    s = d.styles.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = d.styles["Caption"]
    s.font.name = "Arial"; s.font.size = Pt(9); s.font.italic = False; s.font.bold = False
    s.font.color.rgb = RGBColor(0, 0, 0)
    return s


cap_fig, cap_tab = estilo("Cap_Figura"), estilo("Cap_Tabla")
ind = d.styles.add_style("Indice_Figuras_Tablas", WD_STYLE_TYPE.PARAGRAPH)
ind.base_style = d.styles["Normal"]
ind.font.name = "Arial"; ind.font.size = Pt(11)
ind.paragraph_format.line_spacing = 1.15
ind.paragraph_format.space_after = Pt(4)
ind.paragraph_format.tab_stops.add_tab_stop(Cm(16.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

figs, tabs = [], []
for p in ps():
    t = p.text.strip()
    if p.style.name == "Caption" and t.startswith("Figura "):
        p.style = cap_fig; figs.append(t)
    elif p.style.name == "Caption" and t.startswith("Tabla "):
        p.style = cap_tab; tabs.append(t)

# ---------- Referencias a tablas en el texto ----------
def anexar_antes(p_caption_texto, texto):
    for p in ps():
        if p.text.strip() == p_caption_texto:
            nuevo = copy.deepcopy(ps()[0]._p)
            for el in list(nuevo):
                nuevo.remove(el)
            p._p.addprevious(nuevo)
            np_ = Paragraph(nuevo, d)
            np_.style = d.styles["Normal"]
            np_.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            np_.add_run(texto)
            return
    raise ValueError(p_caption_texto)


def cambiar_final(inicio, viejo, nuevo):
    for p in ps():
        if p.text.startswith(inicio):
            for r in reversed(p.runs):
                if viejo in r.text:
                    r.text = r.text.replace(viejo, nuevo)
                    return
    raise ValueError(inicio)


anexar_antes("Tabla 1. Requisitos mínimos de uso.",
             "En la Tabla 1 se presentan los requisitos mínimos necesarios para instalar y utilizar la aplicación.")
cambiar_final("La aplicación cuenta con tres formas de acceso",
              "que le corresponden:", "que le corresponden, como se describe en la Tabla 2:")
cambiar_final("La parte superior muestra la tarjeta",
              "los siguientes colores:", "los colores descritos en la Tabla 3:")
anexar_antes("Tabla 4. Problemas frecuentes y su solución.",
             "En la Tabla 4 se presentan las situaciones más comunes que pueden presentarse al usar la aplicación, "
             "su posible causa y la solución recomendada.")
anexar_antes("Tabla 5. Glosario de términos.",
             "En la Tabla 5 se definen los términos utilizados con mayor frecuencia en este manual.")
cambiar_final("Para dudas sobre turnos", "responsable del sistema:",
              "responsable del sistema, cuyos datos se muestran en la Tabla 6:")

# ---------- Índices de figuras y de tablas ----------
todos = ps()
titulo_contenido = next(p for p in todos if p.text.strip() == "CONTENIDO")
toc_fin = None
for p in todos:
    if p._p.xpath('.//w:fldChar[@w:fldCharType="end"]') and p.style.name.startswith("toc"):
        toc_fin = p
ancla = toc_fin._p


def run_fld(tipo):
    r = OxmlElement("w:r"); f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), tipo); r.append(f); return r


def run_txt(t, tab=False):
    r = OxmlElement("w:r")
    if tab:
        r.append(OxmlElement("w:tab"))
    x = OxmlElement("w:t"); x.set(qn("xml:space"), "preserve"); x.text = t; r.append(x); return r


def salto():
    p = OxmlElement("w:p"); r = OxmlElement("w:r"); b = OxmlElement("w:br"); b.set(qn("w:type"), "page")
    r.append(b); p.append(r); return p


def bloque(titulo, entradas, estilo_cap):
    els = [salto()]
    t = copy.deepcopy(titulo_contenido._p)
    ts = list(t.iter(qn("w:t"))); ts[0].text = titulo
    for x in ts[1:]:
        x.text = ""
    els.append(t)
    for k, e in enumerate(entradas):
        p = OxmlElement("w:p")
        pPr = OxmlElement("w:pPr"); ps_ = OxmlElement("w:pStyle"); ps_.set(qn("w:val"), ind.style_id)
        pPr.append(ps_); p.append(pPr)
        if k == 0:
            p.append(run_fld("begin"))
            r = OxmlElement("w:r"); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
            it.text = f' TOC \\h \\z \\t "{estilo_cap},1" '; r.append(it); p.append(r)
            p.append(run_fld("separate"))
        p.append(run_txt(e))
        p.append(run_txt(str(paginas.get(e, "")), tab=True))
        if k == len(entradas) - 1:
            p.append(run_fld("end"))
        els.append(p)
    return els


# Los dos índices nuevos agregan 2 páginas: ajustar números guardados del contenido general
if paginas:
    for p in todos:
        if p.style.name.startswith("toc"):
            ts = [t for t in p._p.iter(qn("w:t")) if t.text and t.text.strip()]
            if ts and ts[-1].text.strip().isdigit():
                ts[-1].text = str(int(ts[-1].text.strip()) + 2)

nuevos = bloque("ÍNDICE DE FIGURAS", figs, cap_fig.style_id) + bloque("ÍNDICE DE TABLAS", tabs, cap_tab.style_id)
pos = ancla
for el in nuevos:
    pos.addnext(el); pos = el

# Actualizar campos al abrir
st = d.settings.element
uf = st.find(qn("w:updateFields"))
if uf is None:
    uf = OxmlElement("w:updateFields")
    sig = next((st.find(qn(t)) for t in ("w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat",
                                          "w:docVars", "w:rsids") if st.find(qn(t)) is not None), None)
    sig.addprevious(uf) if sig is not None else st.append(uf)
uf.set(qn("w:val"), "true")

d.save(OUT)
json.dump({"figs": figs, "tabs": tabs}, open("/tmp/caps.json", "w"), ensure_ascii=False)
print("ok", len(figs), len(tabs))
