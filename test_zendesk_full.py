from services.zendesk_service import (
    construir_texto_ticket,
    unir_textos,
    mapear_fechas_pdv,
    formatear_fecha_hora
)
from utils.ticket_parser import extraer_pdvs_desde_ticket
from services.pqr_service import generar_presentacion_desde_parser

ticket_id = 9657

#Traer mensajes
mensajes = construir_texto_ticket(ticket_id)

#Une texto
texto = unir_textos(mensajes)

print("\n====== TEXTO LIMPIO ======\n")
print(texto)

#Activa Parser
parsed = extraer_pdvs_desde_ticket(texto)

print("\n====== PARSED ======\n")
print(parsed)

#Mapear fechas
fechas_raw = mapear_fechas_pdv(parsed, mensajes)

#Separar fecha y hora
fechas_por_pdv = {}
horas_por_pdv = {}

for k, v in fechas_raw.items():
    fecha, hora = formatear_fecha_hora(v)
    fechas_por_pdv[k] = fecha
    horas_por_pdv[k] = hora

#Genera slides
presentation_id = generar_presentacion_desde_parser(
    parsed,
    titulo=f"PQR_{ticket_id}",
    ticket_id=ticket_id,
    fechas_por_pdv=fechas_por_pdv,
    horas_por_pdv=horas_por_pdv
)

print("\n====== PRESENTACIÓN ======\n")
print(presentation_id)