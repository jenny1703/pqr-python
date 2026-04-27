from googleapiclient.discovery import build
from services.google_auth import get_credentials


TEMPLATE_ID = "1yaAawlZfRyAhQcKUTtioucWoUqlXqz13KkNxnYLmg-0"


def create_copy(title: str) -> str:
    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    copied_file = drive_service.files().copy(
        fileId=TEMPLATE_ID,
        body={"name": title}
    ).execute()

    return copied_file["id"]


def replace_text(presentation_id: str, data: dict):
    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    requests = []

    for key, value in data.items():
        requests.append({
            "replaceAllText": {
                "containsText": {
                    "text": f"{{{{{key}}}}}",
                    "matchCase": True
                },
                "replaceText": str(value)
            }
        })

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()


if __name__ == "__main__":

    presentation_id = create_copy("PRUEBA PQR")

    data = {
        "TICKET": "9279",
        "FECHA_INGRESO": "04/02",
        "CODIGO_CLIENTE": "122471958",
        "TERRITORIO": "NORORIENTE",
        "JEFATURA": "B2S"
    }

    replace_text(presentation_id, data)

    print("Presentación creada:", presentation_id)