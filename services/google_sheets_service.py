from googleapiclient.discovery import build
from services.google_auth import get_credentials

SHEET_ID = "1qQlDDA8wn730dEns3INnGdmpdTyoB0icfUeIzb-Vgyo"
RANGE_NAME = "Hoja 1!A1:AE10000"


def obtener_datos_por_codigo(codigo_cliente: str, fecha_pqr: str = ""):

    creds = get_credentials()
    sheets_service = build("sheets", "v4", credentials=creds)

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=RANGE_NAME
    ).execute()

    values = result.get("values", [])

    if not values:
        return None

    # 🔹 Normalizar encabezados (minúsculas y sin espacios extra)
    headers = [h.strip().lower() for h in values[0]]

    for row in values[1:]:

        # 🔹 Asegurar que la fila tenga todas las columnas
        row_dict = dict(zip(headers, row + [""] * len(headers)))

        codigo_sheet = str(row_dict.get("cód cliente", "")).strip()

        if codigo_sheet == str(codigo_cliente).strip():

            return {
                "GERENCIA": row_dict.get("gerencia", ""),
                "JEFATURA": row_dict.get("jefatura", ""),
                "TERRITORIO": row_dict.get("territorio", ""),
                "RUTA": row_dict.get("ruta", ""),
                "CANAL": row_dict.get("tipocanal", ""),
                "GEC": row_dict.get("gec1", ""),

                # 🔴 FECHAS (OPCIÓN 1)
                "FECHA_INGRESO": fecha_pqr,
                "FECHA_RESPUESTA": fecha_pqr
            }

    return None