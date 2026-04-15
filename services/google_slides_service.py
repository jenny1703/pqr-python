from googleapiclient.discovery import build
from services.google_auth import get_credentials
import uuid

TEMPLATE_ID = "1yaAawlZfRyAhQcKUTtioucWoUqlXqz13KkNxnYLmg-0"
FOLDER_ID = "16NEQN4eeoFPPVN80QmfnV3JkyKeYlUmA"


# =========================================================
# 🔹 CREAR PRESENTACIÓN DESDE TEMPLATE
# =========================================================
def create_presentation_from_template(title: str) -> str:
    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    copied_file = drive_service.files().copy(
        fileId=TEMPLATE_ID,
        body={"name": title}
    ).execute()

    presentation_id = copied_file["id"]

    # mover a carpeta
    drive_service.files().update(
        fileId=presentation_id,
        addParents=FOLDER_ID,
        removeParents="root",
        fields="id, parents"
    ).execute()

    return presentation_id


# =========================================================
# 🔹 REEMPLAZAR TEXTO EN UN SLIDE ESPECÍFICO
# =========================================================
def replace_text(presentation_id: str, data: dict, slide_id: str = None):

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    requests = []

    for key, value in data.items():

        replace_request = {
            "replaceAllText": {
                "containsText": {
                    "text": f"{{{{{key}}}}}",
                    "matchCase": True
                },
                "replaceText": str(value)
            }
        }

        # 🔴 IMPORTANTE: limitar al slide
        if slide_id:
            replace_request["replaceAllText"]["pageObjectIds"] = [slide_id]

        requests.append(replace_request)

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()


# =========================================================
# 🔹 DUPLICAR SLIDE BASE (UNO NUEVO POR PDV)
# =========================================================
def agregar_o_actualizar_slide(
    presentation_id: str,
    slide_base_id: str,
    codigo_cliente: str,
    descripcion: str
):

    if not slide_base_id:
        raise ValueError("slide_base_id es requerido")

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    codigo_limpio = codigo_cliente.strip()

    # 🔴 ID ÚNICO (CLAVE DEL ARREGLO)
    new_slide_id = f"slide_{codigo_limpio}_{uuid.uuid4().hex[:6]}"

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={
            "requests": [
                {
                    "duplicateObject": {
                        "objectId": slide_base_id,
                        "objectIds": {
                            slide_base_id: new_slide_id
                        }
                    }
                }
            ]
        }
    ).execute()

    return new_slide_id


# =========================================================
# 🔹 ELIMINAR SLIDE BASE (MUY IMPORTANTE)
# =========================================================
def eliminar_slide(presentation_id: str, slide_id: str):

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={
            "requests": [
                {
                    "deleteObject": {
                        "objectId": slide_id
                    }
                }
            ]
        }
    ).execute()