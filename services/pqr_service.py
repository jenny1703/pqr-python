from googleapiclient.discovery import build
from datetime import datetime

from services.google_auth import get_credentials
from services.google_sheets_service import obtener_datos_por_codigo
from services.google_slides_service import (
    create_presentation_from_template,
    agregar_o_actualizar_slide,
    replace_text,
    eliminar_slide
)


def obtener_slide_base(presentation_id):

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    return presentation["slides"][0]["objectId"]


# 🔴 NUEVO: ordenar slides correctamente
def ordenar_slides(presentation_id, slide_ids):

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    requests = []

    for index, slide_id in enumerate(slide_ids):
        requests.append({
            "updateSlidesPosition": {
                "slideObjectIds": [slide_id],
                "insertionIndex": index
            }
        })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()


def generar_presentacion_desde_parser(
    parsed_data,
    titulo,
    ticket_id,
    fechas_por_pdv=None,
    horas_por_pdv=None
):

    fecha_actual = datetime.now().strftime("%d/%m")

    # =========================
    # 🔴 CASO SIN PDV
    # =========================
    if not parsed_data["pdvs"]:

        presentation_id = create_presentation_from_template(titulo)
        slide_base_id = obtener_slide_base(presentation_id)

        new_slide_id = agregar_o_actualizar_slide(
            presentation_id,
            slide_base_id,
            "SIN_PDV",
            "No se encontró código cliente en el ticket"
        )

        replace_text(
            presentation_id,
            {
                "TICKET": str(ticket_id),
                "CODIGO_CLIENTE": "N/A",
                "MENSAJE": "No se encontró código cliente en el ticket",
                "GERENCIA": "",
                "JEFATURA": "",
                "TERRITORIO": "",
                "RUTA": "",
                "CANAL": "",
                "GEC": "",
                "FECHA_INGRESO": fecha_actual,
                "HORA_INGRESO": "",
                "FECHA_RESPUESTA": ""
            },
            slide_id=new_slide_id
        )

        eliminar_slide(presentation_id, slide_base_id)
        return presentation_id

    # =========================
    # 🔹 FLUJO NORMAL
    # =========================

    presentation_id = create_presentation_from_template(titulo)
    slide_base_id = obtener_slide_base(presentation_id)

    contador = 0
    slides_creados = []

    for codigo, data in parsed_data["pdvs"].items():

        descripciones = data.get("descripcion", [])
        if not descripciones:
            continue

        contador += 1

        # 🔴 Ticket dinámico
        if contador == 1:
            ticket_label = str(ticket_id)
        else:
            ticket_label = f"{ticket_id}.{contador-1}"

        # 🔴 Fecha y hora por PDV
        fecha_pdv = ""
        hora_pdv = ""

        if fechas_por_pdv:
            fecha_pdv = fechas_por_pdv.get(codigo, "")

        if horas_por_pdv:
            hora_pdv = horas_por_pdv.get(codigo, "")

        descripcion_texto = "\n".join(f"- {d}" for d in descripciones)

        datos_extra = obtener_datos_por_codigo(codigo) or {}

        # 🔴 Crear slide
        new_slide_id = agregar_o_actualizar_slide(
            presentation_id,
            slide_base_id,
            codigo,
            descripcion_texto
        )

        slides_creados.append(new_slide_id)

        # 🔴 Reemplazo
        replace_text(
            presentation_id,
            {
                "TICKET": ticket_label,
                "CODIGO_CLIENTE": codigo,
                "MENSAJE": descripcion_texto,
                "GERENCIA": datos_extra.get("GERENCIA", ""),
                "JEFATURA": datos_extra.get("JEFATURA", ""),
                "TERRITORIO": datos_extra.get("TERRITORIO", ""),
                "RUTA": datos_extra.get("RUTA", ""),
                "CANAL": datos_extra.get("CANAL", ""),
                "GEC": datos_extra.get("GEC", ""),
                "FECHA_INGRESO": fecha_pdv,
                "HORA_INGRESO": hora_pdv,
                "FECHA_RESPUESTA": ""
            },
            slide_id=new_slide_id
        )

    # 🔴 ORDENAR SLIDES (SOLUCIÓN FINAL)
    ordenar_slides(presentation_id, slides_creados)

    # 🔴 ELIMINAR SLIDE BASE
    eliminar_slide(presentation_id, slide_base_id)

    return presentation_id