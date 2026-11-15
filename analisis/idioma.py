"""Idioma de la respuesta según el encabezado Accept-Language que envía la app ("es" o "en").

La base de datos guarda siempre los nombres en español; lo que se devuelve se arma en el idioma pedido.
"""
from data.ecocrop import cargar_cultivos


def idioma(request):
    return "en" if request.headers.get("Accept-Language", "").strip().lower().startswith("en") else "es"


def nombre_rotacion(ids, idioma_="es"):
    """["papa", "maiz"] -> "Papa → Maíz" (o "Potato → Maize")."""
    por_id = {c["id"]: c for c in cargar_cultivos()}
    campo = "nombre_en" if idioma_ == "en" else "nombre"
    return " → ".join(por_id[i][campo] if i in por_id else i for i in ids)


def traducir_rotacion(texto, idioma_="es"):
    """"Papa → Maíz" guardado en la base -> en el idioma pedido (lo que no se reconoce queda igual)."""
    if idioma_ != "en" or not texto:
        return texto
    por_nombre = {c["nombre"]: c["nombre_en"] for c in cargar_cultivos()}
    return " → ".join(por_nombre.get(p.strip(), p.strip()) for p in texto.split("→"))
