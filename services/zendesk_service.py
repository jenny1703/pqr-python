import requests
import re
from datetime import datetime
from datetime import datetime
import pytz

SUBDOMAIN = "xxxxxx"
EMAIL = "xxxxxx@xxxxx.com"
API_TOKEN = "xxxxxx"

BASE_URL = f"https://{SUBDOMAIN}.zendesk.com/api/v2"


def obtener_comentarios_ticket(ticket_id):

    url = f"{BASE_URL}/tickets/{ticket_id}/comments.json"

    response = requests.get(
        url,
        auth=(f"{EMAIL}/token", API_TOKEN)
    )

    if response.status_code != 200:
        raise Exception(f"Error Zendesk comments: {response.status_code}")

    return response.json().get("comments", [])


def limpiar_mensaje(body: str):

    lineas = body.splitlines()
    salida = []

    for l in lineas:

        l_lower = l.lower()

        if any(x in l_lower for x in ["cargó:", "url:", "tipo:", "tamaño:"]):
            continue

        l = re.sub(r"\(\d{2}:\d{2}:\d{2}\)", "", l)
        l = re.sub(r"^[^:]+:\s*", "", l)

        l = l.strip()

        if l:
            salida.append(l)

    return "\n".join(salida)


def construir_texto_ticket(ticket_id):

    comentarios = obtener_comentarios_ticket(ticket_id)

    mensajes = []

    for c in comentarios:

        body = c.get("plain_body", "").strip()
        fecha = c.get("created_at")

        if not body:
            continue

        limpio = limpiar_mensaje(body)

        if limpio:
            mensajes.append({
                "texto": limpio,
                "fecha": fecha
            })

    return mensajes


def unir_textos(mensajes):
    return "\n".join(m["texto"] for m in mensajes)


def mapear_fechas_pdv(parsed, mensajes):

    resultado = {}

    for m in mensajes:
        texto = m["texto"]
        fecha = m["fecha"]

        for codigo in parsed["pdvs"].keys():
            if codigo in texto:
                resultado[codigo] = fecha

    return resultado


def formatear_fecha_hora(fecha_str):

    if not fecha_str:
        return "", ""

    # UTC (Zendesk)
    fecha_utc = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ")

    # Convertir a zona Colombia
    utc = pytz.utc
    colombia = pytz.timezone("America/Bogota")

    fecha_utc = utc.localize(fecha_utc)
    fecha_local = fecha_utc.astimezone(colombia)

    return (
        fecha_local.strftime("%d/%m"),
        fecha_local.strftime("%H:%M")
    )
