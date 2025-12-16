from src.utils.files import leer_archivo

import json

def validar_cedula(envelope):
    try:
        print(envelope)
        print(type(envelope))
        data_str = envelope.get("data")
        if not data_str:
            print("❌ No hay data en el request")
            return False

        url_identificacion = envelope.get("urlIdentificacion")
        print(f"📂 Intentando leer: {url_identificacion}")

        file_content = leer_archivo(url_identificacion)

        if isinstance(file_content, bytes):
            print(f"✅ Archivo leído correctamente. Tamaño: {len(file_content)} bytes")
            print(f"Tipo de dato: {type(file_content)}")
            return True
        else:
            print("❌ Error: No se pudo leer el archivo (retornó None)")
            return False
        
    except Exception as e:
        print(f"❌ Excepción en validar_cedula: {e}")
        return False