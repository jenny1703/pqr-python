import re

def extraer_pdvs_desde_ticket(mensaje: str):

    lineas = [l.strip() for l in mensaje.splitlines() if l.strip()]
    pdvs = {}

    codigo_actual = None
    dentro_pdv = False

    def es_ruido(texto: str) -> bool:
        texto_lower = texto.lower()

        frases_bot = [
            "gracias por comunicarse",
            "centro de ayuda",
            "le estaremos dando solución",
            "tenga en cuenta ser específico",
            "48 horas hábiles",
            "numero de contacto",
            "correo electrónico",
            "indiquenos la siguiente información"
        ]

        return (
            texto_lower in ["pdv", "avatar"] or
            "ayer" in texto_lower or
            "sábado" in texto_lower or
            re.fullmatch(r"[•⏳:.\-0-9\s]+", texto) or
            any(frase in texto_lower for frase in frases_bot)
        )

    i = 0
    while i < len(lineas):

        linea = lineas[i]
        linea_lower = linea.lower()

        #DETECTA EL CÓDIGO
    
        match_codigo = re.search(r"(?:cod\s*)?(\b12\d{8}\b)", linea_lower)

        if match_codigo:

            codigo_detectado = match_codigo.group(1)

            #evitar teléfonos
            if any(x in linea_lower for x in [
                "número de contacto",
                "numero de contacto",
                "telefono",
                "teléfono",
                "celular"
            ]):
                i += 1
                continue

            codigo_actual = codigo_detectado

            if codigo_actual not in pdvs:
                pdvs[codigo_actual] = {"descripcion": []}

            #capturar texto en la misma línea
            texto_restante = re.sub(r"(?:cod\s*)?\b12\d{8}\b", "", linea_lower).strip()

            if texto_restante and len(texto_restante) > 20:
                if texto_restante not in pdvs[codigo_actual]["descripcion"]:
                    pdvs[codigo_actual]["descripcion"].append(texto_restante)

            i += 1
            continue

        
        #BLOQUE PDV
        
        if linea == "PDV":
            dentro_pdv = True
            codigo_actual = None
            i += 1
            continue

        if dentro_pdv and not codigo_actual:
            match_codigo = re.search(r"\b12\d{8}\b", linea)
            if match_codigo:
                codigo_actual = match_codigo.group()

                if codigo_actual not in pdvs:
                    pdvs[codigo_actual] = {"descripcion": []}

            i += 1
            continue

       
        #INDICADORES
        
        if "el cliente en el indicador" in linea_lower:

            if codigo_actual:
                if linea not in pdvs[codigo_actual]["descripcion"]:
                    pdvs[codigo_actual]["descripcion"].append(linea)

            i += 1
            continue

        
        # PDV: + TEXTO LIBRE
        
        if "pdv:" in linea_lower:

            match = re.search(r"\b12\d{8}\b", linea)
            if match:
                codigo_actual = match.group()

                if codigo_actual not in pdvs:
                    pdvs[codigo_actual] = {"descripcion": []}

                j = i + 1
                descripcion = []

                while j < len(lineas):

                    siguiente = lineas[j]
                    siguiente_lower = siguiente.lower()

                    if re.search(r"\b12\d{8}\b", siguiente):
                        break

                    if any(x in siguiente_lower for x in [
                        "mes de medición",
                        "nombre",
                        "correo",
                        "número de contacto"
                    ]):
                        j += 1
                        continue

                    if es_ruido(siguiente) and len(siguiente) < 40:
                        j += 1
                        continue

                    descripcion.append(siguiente)
                    j += 1

                if descripcion:
                    texto_final = " ".join(descripcion)

                    if texto_final not in pdvs[codigo_actual]["descripcion"]:
                        pdvs[codigo_actual]["descripcion"].append(texto_final)

            i += 1
            continue

        
        #RECLAMACIÓN
    
        if "reclamación" in linea_lower:

            j = i + 1
            descripcion = []

            while j < len(lineas):

                siguiente = lineas[j]

                if re.search(r"\b12\d{8}\b", siguiente):
                    break

                if es_ruido(siguiente) and len(siguiente) < 40:
                    j += 1
                    continue

                descripcion.append(siguiente)
                j += 1

            if codigo_actual and descripcion:
                texto_final = " ".join(descripcion)

                if texto_final not in pdvs[codigo_actual]["descripcion"]:
                    pdvs[codigo_actual]["descripcion"].append(texto_final)

            i += 1
            continue

        
        #TEXTO LIBRE GENERAL
        
        if codigo_actual:

            if es_ruido(linea):
                i += 1
                continue

            if any(x in linea_lower for x in [
                "mes de medición",
                "nombre",
                "correo",
                "número de contacto"
            ]):
                i += 1
                continue

            if len(linea) < 40:
                i += 1
                continue

            if linea not in pdvs[codigo_actual]["descripcion"]:
                pdvs[codigo_actual]["descripcion"].append(linea)

            i += 1
            continue

        i += 1

    return {"pdvs": pdvs}