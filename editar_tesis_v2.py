import copy
import re
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "/app/tesis_v2.docx"
OUT = "/app/Tesis_Final.docx"
BM = "_TocOrg0001"
CAP = "Figura 1. Organigrama del Comisariado Ejidal de San José Carpinteros."

d = Document(SRC)
P = d.paragraphs
body = d.element.body


def set_text(par, texto):
    runs = par.runs
    runs[0].text = texto
    for r in runs[1:]:
        r.text = ""


# ---------- 1. Fila de multas (Tabla 1) ----------
fila = d.tables[0].rows[4]
set_text(fila.cells[2].paragraphs[0], "Gestión y control de multas")
set_text(fila.cells[3].paragraphs[0],
         "Número de multas generadas y número de multas pagadas registradas en el sistema "
         "(porcentaje de cumplimiento de pago = multas pagadas / multas generadas × 100)")
set_text(fila.cells[4].paragraphs[0], "Razón (frecuencia y %)")

# ---------- 2. Renumerar figuras existentes (+1) ----------
inc = lambda m: f"{m.group(1)}{int(m.group(2)) + 1}"
pat = re.compile(r"(Figuras? )(\d+)")
toc_fig = [p for p in P[100:120] if p.text.startswith("Figura ")]
for p in toc_fig:
    for t in p._p.iter(qn("w:t")):
        if t.text and t.text.startswith("Figura "):
            t.text = pat.sub(inc, t.text, count=1)
for p in P[162:]:
    for r in p.runs:
        if "Figura" in r.text:
            r.text = pat.sub(inc, r.text)

# Entrada nueva en el índice de figuras
# (la primera entrada contiene el inicio del campo TOC: se reutiliza para la figura nueva
#  y se agrega una copia de la segunda entrada para la antigua Figura 1)
def reapuntar(p, bm, texto, pagina):
    for el in p.iter():
        if el.get(qn("w:anchor")):
            el.set(qn("w:anchor"), bm)
        if el.tag == qn("w:instrText") and "PAGEREF" in (el.text or ""):
            el.text = re.sub(r"_Toc\d+", bm, el.text)
    ts = list(p.iter(qn("w:t")))
    ts[0].text = texto
    ts[-1].text = pagina


primera = toc_fig[0]._p
ts0 = list(primera.iter(qn("w:t")))
texto_ant, pag_ant = ts0[0].text, ts0[-1].text
bm_ant = re.search(r"PAGEREF (_Toc\d+)", "".join(e.text or "" for e in primera.iter(qn("w:instrText")))).group(1)
nuevo = copy.deepcopy(toc_fig[1]._p)
reapuntar(nuevo, bm_ant, texto_ant, pag_ant)
reapuntar(primera, BM, CAP, "6")
primera.addnext(nuevo)

# ---------- 3. Organigrama en 1.2.1 ----------
p157 = P[157]
for r in p157.runs:
    if "siguiente manera:" in r.text:
        r.text = r.text.replace("siguiente manera:", "siguiente manera (véase la Figura 1):")

# El organigrama ya fue pegado por el usuario en este párrafo
img_p = P[162]
assert img_p._p.xpath(".//w:drawing")
img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
img_p.paragraph_format.keep_with_next = True

cap = copy.deepcopy(P[370]._p)
for tag in ("w:bookmarkStart", "w:bookmarkEnd"):
    for el in cap.findall(qn(tag)):
        cap.remove(el)
for r in cap.findall(qn("w:r")):
    if r.xpath(".//w:drawing") or r.find(qn("w:br")) is not None:
        cap.remove(r)
cts = list(cap.iter(qn("w:t")))
cts[0].text = CAP
for t in cts[1:]:
    t.text = ""
bs = OxmlElement("w:bookmarkStart")
bs.set(qn("w:id"), "9001")
bs.set(qn("w:name"), BM)
be = OxmlElement("w:bookmarkEnd")
be.set(qn("w:id"), "9001")
cap.find(qn("w:pPr")).addnext(bs)
cap.append(be)
img_p._p.addnext(cap)

# ---------- 4. Cronograma en hoja horizontal ----------
crono = d.tables[8]._tbl
repo = d.tables[9]._tbl
kids = list(body)
i_tb = kids.index(crono)
i_tx = max(i for i in range(i_tb) if kids[i].xpath(".//w:txbxContent"))
p_txbx = kids[i_tx]           # cuadro de texto con datos del estudiante
p_salto = kids[i_tx - 1]      # párrafo con salto de página
assert p_txbx.xpath(".//w:txbxContent") and p_salto.xpath(".//w:br")

final_sect = body.find(qn("w:sectPr"))


def nueva_sect(horizontal):
    s = copy.deepcopy(final_sect)
    if horizontal:
        pg = s.find(qn("w:pgSz"))
        pg.set(qn("w:w"), "15840")
        pg.set(qn("w:h"), "12240")
        pg.set(qn("w:orient"), "landscape")
        mar = s.find(qn("w:pgMar"))
        for k, v in (("top", "850"), ("bottom", "850"), ("left", "1418"), ("right", "1418"),
                     ("header", "425"), ("footer", "425")):
            mar.set(qn(f"w:{k}"), v)
    return s


def poner_sect(p, sect):
    pPr = p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p.insert(0, pPr)
    pPr.append(sect)


# Fin de la sección vertical anterior (conserva el inicio de numeración original)
for r in p_salto.findall(qn("w:r")):
    if r.find(qn("w:br")) is not None:
        p_salto.remove(r)
poner_sect(p_salto, nueva_sect(False))

# Las secciones siguientes continúan la numeración
pn = final_sect.find(qn("w:pgNumType"))
if pn is not None:
    final_sect.remove(pn)

# Quitar párrafos vacíos sobrantes alrededor del cronograma
k = list(body)
for el in [k[i_tb + 1], k[i_tb + 2]]:
    if el.tag == qn("w:p") and not "".join(el.itertext()).strip():
        body.remove(el)

# Fin de la sección horizontal: primer párrafo después de la tabla de reportes
sig = repo.getnext()
if sig is None or sig.tag != qn("w:p"):
    sig = OxmlElement("w:p")
    repo.addnext(sig)
poner_sect(sig, nueva_sect(True))

# Ajustar anchos y altos de las tablas a la hoja horizontal (24.4 cm útiles)
def ajustar(tbl, anchos, alto=None):
    grid = tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), anchos):
        gc.set(qn("w:w"), str(int(w * 567)))
    tblW = tbl.find(qn("w:tblPr")).find(qn("w:tblW"))
    if tblW is not None:
        tblW.set(qn("w:w"), str(int(sum(anchos) * 567)))
        tblW.set(qn("w:type"), "dxa")
    for tr in tbl.findall(qn("w:tr")):
        col = 0
        for tc in tr.findall(qn("w:tc")):
            tcPr = tc.find(qn("w:tcPr"))
            span = tcPr.find(qn("w:gridSpan")) if tcPr is not None else None
            n = int(span.get(qn("w:val"))) if span is not None else 1
            w = sum(anchos[col:col + n])
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is not None:
                tcW.set(qn("w:w"), str(int(w * 567)))
                tcW.set(qn("w:type"), "dxa")
            col += n
        if alto:
            h = tr.find(qn("w:trPr")).find(qn("w:trHeight"))
            h.set(qn("w:val"), str(int(alto * 567)))


ajustar(crono, [9.7, 1.3] + [2.68] * 5, alto=0.3)
ajustar(repo, [3.4, 8.0] + [4.33] * 3)
filas_rep = repo.findall(qn("w:tr"))
for tr, h in zip(filas_rep, [0.7, 0.8, 0.55, 0.55, 0.55, 0.55]):
    trPr = tr.find(qn("w:trPr"))
    if trPr is None:
        trPr = OxmlElement("w:trPr")
        tr.insert(0, trPr)
    th = trPr.find(qn("w:trHeight"))
    if th is None:
        th = OxmlElement("w:trHeight")
        trPr.append(th)
    th.set(qn("w:val"), str(int(h * 567)))
DESPUES_SZ = ["w:highlight", "w:u", "w:effect", "w:bdr", "w:shd", "w:fitText", "w:vertAlign",
              "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout", "w:specVanish", "w:oMath"]
for tbl, tam in ((crono, "14"), (repo, "16")):
    for rPr in tbl.iter(qn("w:rPr")):
        for t in ("w:szCs", "w:sz"):
            e = rPr.find(qn(t))
            if e is None:
                e = OxmlElement(t)
                if t == "w:szCs" or rPr.find(qn("w:szCs")) is None:
                    sig_r = next((rPr.find(qn(x)) for x in DESPUES_SZ if rPr.find(qn(x)) is not None), None)
                else:
                    sig_r = rPr.find(qn("w:szCs"))
                if sig_r is not None:
                    sig_r.addprevious(e)
                else:
                    rPr.append(e)
            e.set(qn("w:val"), tam)
for tbl in (crono, repo):
    for pp in tbl.iter(qn("w:p")):
        sp = pp.find(qn("w:pPr"))
        if sp is None:
            sp = OxmlElement("w:pPr")
            pp.insert(0, sp)
        s = sp.find(qn("w:spacing"))
        if s is None:
            s = OxmlElement("w:spacing")
            sig_p = next((sp.find(qn(x)) for x in ("w:ind", "w:contextualSpacing", "w:mirrorIndents",
                          "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
                          "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
                          "w:sectPr", "w:pPrChange") if sp.find(qn(x)) is not None), None)
            if sig_p is not None:
                sig_p.addprevious(s)
            else:
                sp.append(s)
        s.set(qn("w:before"), "0")
        s.set(qn("w:after"), "0")
        s.set(qn("w:line"), "240")
        s.set(qn("w:lineRule"), "auto")
        # tamaño de la marca de párrafo (celdas vacías)
        prp = sp.find(qn("w:rPr"))
        if prp is None:
            prp = OxmlElement("w:rPr")
            sig_s = sp.find(qn("w:sectPr")) if sp.find(qn("w:sectPr")) is not None else sp.find(qn("w:pPrChange"))
            if sig_s is not None:
                sig_s.addprevious(prp)
            else:
                sp.append(prp)
        for t in ("w:sz", "w:szCs"):
            if prp.find(qn(t)) is None:
                e = OxmlElement(t)
                e.set(qn("w:val"), "14")
                sig_r = next((prp.find(qn(x)) for x in (["w:szCs"] if t == "w:sz" else []) + DESPUES_SZ
                              if prp.find(qn(x)) is not None), None)
                if sig_r is not None:
                    sig_r.addprevious(e)
                else:
                    prp.append(e)

# ---------- 5. Pedir a Word actualizar índices al abrir ----------
st = d.settings.element
uf = st.find(qn("w:updateFields"))
if uf is None:
    uf = OxmlElement("w:updateFields")
    sig_el = next((st.find(qn(t)) for t in ("w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr",
                                             "w:compat", "w:docVars", "w:rsids")
                   if st.find(qn(t)) is not None), None)
    if sig_el is not None:
        sig_el.addprevious(uf)
    else:
        st.append(uf)
uf.set(qn("w:val"), "true")

d.save(OUT)
print("ok")
