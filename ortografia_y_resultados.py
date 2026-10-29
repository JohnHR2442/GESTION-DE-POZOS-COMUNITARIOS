"""Corrige ortografía de la tesis y agrega el párrafo final de Resultados (publicación en Google Play).
Uso: python ortografia_y_resultados.py entrada.docx salida.docx"""
import sys, copy, re
from docx import Document
from docx.text.paragraph import Paragraph

SRC, DST = sys.argv[1:3]

CORRECCIONES = [
    (r"\bGESTION\b", "GESTIÓN"),
    (r"\bINGENIERIA\b", "INGENIERÍA"),
    (r"\bLOPEZ\b", "LÓPEZ"),
    (r"\bHipotesis\b", "Hipótesis"),
    (r"\bPoblacion\b", "Población"),
    (r"problema mas importante", "problema más importante"),
    (r"servicios  Apis REST", "servicios API REST"),
    (r"\bMartinez, M\. G\.", "Martínez, M. G."),
    (r"\badminsitración\b", "administración"),
    (r"\bCapitulo\b", "Capítulo"),
    (r"\bTitulo 2\b", "Título 2"),
    (r"\btitulo\b", "título"),
    (r"se utilizara el", "se utilizará el"),
    (r"\bFormulas:", "Fórmulas:"),
    (r"Usa r el", "Usar el"),
    (r"demás paginas", "demás páginas"),
    (r"de la pagina web", "de la página web"),
    (r"Se encerarán en", "Se encerrarán en"),
    (r"Se enlistaran en", "Se enlistarán en"),
]

RESULTADO_FINAL = (
    "Finalmente, como evidencia del cumplimiento del objetivo de publicación, la aplicación "
    "“Gestión de Pozos Comunitarios” superó la fase de pruebas cerradas en Google Play Console y fue "
    "liberada en la versión de producción de la tienda Google Play, bajo la cuenta de desarrollador "
    "“Gestión Agrícola Escolar”. Con ello, los socios y contadores de los pozos San Isidro, Zapata y "
    "Cárdenas pueden localizarla escribiendo su nombre en el buscador de la tienda, instalarla de forma "
    "gratuita en su teléfono Android y comenzar a utilizarla sin intermediarios ni configuraciones "
    "adicionales, tal como se muestra en las Figuras 1 y 2 del manual de usuario (Anexo A). Este "
    "resultado confirma que el sistema dejó de ser un prototipo para convertirse en una herramienta en "
    "operación real, disponible de manera permanente para las comunidades participantes."
)

d = Document(SRC)


def todos_los_parrafos():
    vistos = set()
    partes = [d.element.body]
    for s in d.sections:
        for hf in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            if not hf.is_linked_to_previous:
                partes.append(hf._element)
    for raiz in partes:
        for p in raiz.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            if p not in vistos:
                vistos.add(p)
                yield Paragraph(p, None)


hechos, pendientes = {}, []
for p in todos_los_parrafos():
    for patron, nuevo in CORRECCIONES:
        if not re.search(patron, p.text):
            continue
        ok = False
        for r in p.runs:
            if re.search(patron, r.text):
                r.text = re.sub(patron, nuevo, r.text)
                ok = True
        if not ok:  # la palabra está repartida en varias partes: unir el texto en la primera
            runs = p.runs
            texto = re.sub(patron, nuevo, "".join(r.text for r in runs))
            if runs:
                runs[0].text = texto
                for r in runs[1:]:
                    r.text = ""
                ok = True
        if ok:
            hechos[nuevo] = hechos.get(nuevo, 0) + 1
        else:
            pendientes.append((patron, p.text[:60]))

# Párrafo final de Resultados (antes de CONCLUSIONES)
modelo = next(p for p in d.paragraphs if p.text.startswith("En conjunto, estos elementos quedan fuera del alcance"))
nuevo_p = copy.deepcopy(modelo._p)
modelo._p.addnext(nuevo_p)
np_ = Paragraph(nuevo_p, modelo._parent)
runs = np_.runs
runs[0].text = RESULTADO_FINAL
for r in runs[1:]:
    r._r.getparent().remove(r._r)
# párrafo vacío de separación, como en el resto del documento
modelo._p.addnext(copy.deepcopy(modelo._p.getnext().getnext()) if False else Paragraph(copy.deepcopy(modelo._p), None)._p)
sep = modelo._p.getnext()
for r in list(sep.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')):
    r.getparent().remove(r)

d.save(DST)
for k, v in hechos.items():
    print(f"{v:3d}  -> {k}")
print("Pendientes:", pendientes)
