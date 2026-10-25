import re
import glob

M = {
    "dia": "día", "dias": "días", "sesion": "sesión", "contrasena": "contraseña", "contrasenas": "contraseñas",
    "codigo": "código", "digitos": "dígitos", "enviara": "enviará", "dara": "dará", "actualizo": "actualizó",
    "numero": "número", "telefono": "teléfono", "recibiras": "recibirás", "llegaran": "llegarán",
    "notificacion": "notificación", "electronico": "electrónico", "olvido": "olvidó", "cuantas": "cuántas",
    "tuberia": "tubería", "presion": "presión", "notificara": "notificará", "ano": "año", "anos": "años",
    "estadisticas": "estadísticas", "descripcion": "descripción", "valido": "válido", "invalido": "inválido",
    "razon": "razón", "rotacion": "rotación", "aun": "aún", "mas": "más", "aqui": "aquí", "ultima": "última",
    "ultimo": "último", "informacion": "información", "publico": "público", "automaticamente": "automáticamente",
    "indico": "indicó", "caido": "caído", "accion": "acción", "solicito": "solicitó", "asigno": "asignó",
    "laborara": "laborará", "recuperacion": "recuperación", "creacion": "creación", "unicamente": "únicamente",
    "gestion": "gestión", "aplicacion": "aplicación", "actualizacion": "actualización", "traves": "través",
    "mensajeria": "mensajería", "configuracion": "configuración", "conservacion": "conservación",
    "eliminacion": "eliminación", "politica": "política", "envia": "envía", "seleccion": "selección",
    "proximo": "próximo", "proxima": "próxima", "despues": "después", "tambien": "también", "podras": "podrás",
    "atras": "atrás", "pagina": "página", "minimo": "mínimo", "exito": "éxito", "ningun": "ningún",
}
FRASES = [("Se envio", "Se envió"), ("el envio", "el envío"), ("Si, eliminar", "Sí, eliminar"),
          ("se marco como", "se marcó como"), ("ya esta marcado", "ya está marcado"),
          ("no esta configurado", "no está configurado"), ("cuenta este activa", "cuenta esté activa"),
          ("Como usamos", "Cómo usamos"), ("Con quien", "Con quién")]
PAL = re.compile(r"\b(" + "|".join(M) + r")\b", re.I)


def corrige(t):
    def f(m):
        w = m.group(1)
        n = M[w.lower()]
        return n.capitalize() if w[0].isupper() else n
    t = PAL.sub(f, t)
    for a, b in FRASES:
        t = t.replace(a, b)
    return t


def es_texto(seg):
    if not seg or seg.startswith(("/", "tel:", "#", "http")) or "-" in seg.split(" ")[0] and " " not in seg:
        return False
    return " " in seg.strip() or seg[:1].isupper()


cambios = 0
archivos = glob.glob("/app/frontend/app/**/*.tsx", recursive=True) + glob.glob("/app/frontend/src/**/*.tsx", recursive=True) + ["/app/backend/server.py"]
for f in archivos:
    lineas = open(f, encoding="utf-8").read().split("\n")
    nuevo = []
    for l in lineas:
        s = l.strip()
        if s.startswith(("import", "//", "#", "*", "from ")):
            nuevo.append(l); continue
        orig = l
        segs = [m for m in re.finditer(r'"([^"\n]*)"|`([^`\n]*)`|>([^<>{}\n]+)<', l)]
        for m in reversed(segs):
            g = next(i for i in (1, 2, 3) if m.group(i) is not None)
            seg = m.group(g)
            if es_texto(seg):
                l = l[:m.start(g)] + corrige(seg) + l[m.end(g):]
        # texto JSX en líneas propias (sin código)
        if f.endswith(".tsx") and s and not re.search(r"[=;(){}<>\[\]:\"'`]", s) and " " in s:
            l = l.replace(s, corrige(s))
        if l != orig:
            cambios += 1
        nuevo.append(l)
    open(f, "w", encoding="utf-8").write("\n".join(nuevo))
print("lineas cambiadas", cambios)
