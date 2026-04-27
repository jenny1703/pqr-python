from fastapi import FastAPI

from services.zendesk_service import (
    construir_texto_ticket,
    unir_textos,
    mapear_fechas_pdv,
    formatear_fecha_hora
)
from utils.ticket_parser import extraer_pdvs_desde_ticket
from services.pqr_service import generar_presentacion_desde_parser

app = FastAPI()


@app.get("/")
def home():
    return {"status": "API PQR funcionando"}


#acepta GET y POST
@app.api_route("/procesar_ticket/{ticket_id}", methods=["GET", "POST"])
def procesar_ticket(ticket_id: int):

    try:
        
        #TRAER MENSAJES ZENDESK
        
        mensajes = construir_texto_ticket(ticket_id)

        if not mensajes:
            return {"error": "No hay mensajes en el ticket"}

       
        #UNIR TEXTO
    
        texto = unir_textos(mensajes)

        
        #PARSER
        
        parsed = extraer_pdvs_desde_ticket(texto)

        if not parsed["pdvs"]:
            return {"error": "No se encontraron PDVs"}

    
        #FECHAS POR PDV
    
        fechas_raw = mapear_fechas_pdv(parsed, mensajes)

        fechas_por_pdv = {}
        horas_por_pdv = {}

        for codigo, fecha_raw in fechas_raw.items():
            fecha, hora = formatear_fecha_hora(fecha_raw)
            fechas_por_pdv[codigo] = fecha
            horas_por_pdv[codigo] = hora

        
        #GENERAR PRESENTACIÓN
        
        presentation_id = generar_presentacion_desde_parser(
            parsed,
            titulo=f"PQR_{ticket_id}",
            ticket_id=ticket_id,
            fechas_por_pdv=fechas_por_pdv,
            horas_por_pdv=horas_por_pdv
        )

        return {
            "ok": True,
            "ticket": ticket_id,
            "presentation_id": presentation_id
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }