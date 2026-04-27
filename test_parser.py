# test_parser.py

from utils.ticket_parser import extraer_pdvs_desde_ticket
from services.pqr_service import generar_presentacion_desde_parser
from datetime import datetime

mensaje = """
Pdv : 1210617655
ME DE MEDICION: Abril 
NOMBRE: RICHAR IVAN CORPAS
CORREO:  Ivan.29.05.18@gmail.com
NUMERO: 3152768230

Validar el tema de portafolio se evidencia está al 100%

2 . Validar por favor el bono no calóricos ya que está implementado como se evidencia en la siguiente foto
"""

#Parsear
parsed = extraer_pdvs_desde_ticket(mensaje)

print("\n====== PARSED ======\n")
for codigo, datos in parsed["pdvs"].items():
    print(f"  {codigo}:")
    for desc in datos["descripcion"]:
        print(f"    → {desc}")

#Generar slides
if parsed["pdvs"]:
    ticket_id    = 9657
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    titulo       = f"PQR_{ticket_id}"

    print(f"\n====== GENERANDO PRESENTACIÓN: {titulo} ======\n")

    presentation_id = generar_presentacion_desde_parser(
        parsed,
        titulo=titulo,
        ticket_id=ticket_id
    )

    print(f"Presentación creada: {presentation_id}")
    print(f"https://docs.google.com/presentation/d/{presentation_id}/edit")

else:
    print("\nNo se encontraron PDVs — no se genera presentación")