import numpy as np
import cv2
import zxingcpp
import re
def leer_qr_code(img):
    """
    Lee códigos QR de la imagen usando ZXing.
    """
    if not isinstance(img, np.ndarray):
        img = np.array(img)

    if img.dtype != np.uint8:
        img = img.astype(np.uint8)

    if img.ndim == 3:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img

    results = zxingcpp.read_barcodes(img_rgb)

    # Buscar QR Code
    for r in results:
        if r.format.name == "QRCode" and r.text:
            return r.text

    return None

def extraer_datos_qr(raw: str) -> dict:
    """
    Extrae datos del QR. El formato puede variar, pero generalmente
    contiene datos separados por caracteres especiales o en JSON.
    """
    
    # Intentar parsear como JSON primero
    try:
        import json
        data = json.loads(raw)
        return {
            "cedula": data.get("numeroDocumento") or data.get("cedula"),
            "apellidos": data.get("apellidos"),
            "nombres": data.get("nombres"),
            "fecha_nacimiento": data.get("fechaNacimiento"),
            "sexo": data.get("sexo"),
            "formato": "JSON"
        }
    except:
        pass
    
    # Si no es JSON, intentar parsear como texto delimitado
    # Similar al PDF417
    s = raw.replace("\x00", "|").replace("<NUL>", "|")
    s = re.sub(r"\|+", "|", s)
    parts = [p.strip() for p in s.split("|") if p.strip()]
    
    cedula = next((p for p in parts if re.fullmatch(r"\d{8,10}", p)), None)
    letras = [p for p in parts if re.fullmatch(r"[A-ZÁÉÍÓÚÑ]+", p) and len(p) >= 3]
    
    apellidos = None
    nombres = None
    
    if len(letras) >= 2:
        apellidos = letras[0]
        nombres = " ".join(letras[1:])
    
    sexo = None
    fecha_nacimiento = None
    sexo_fecha_match = re.search(r"[01]?([MF])(\d{8})", raw)
    if sexo_fecha_match:
        sexo = sexo_fecha_match.group(1)
        fecha_nacimiento = sexo_fecha_match.group(2)
    
    return {
        "cedula": cedula,
        "apellidos": apellidos,
        "nombres": nombres,
        "fecha_nacimiento": fecha_nacimiento,
        "sexo": sexo,
        "formato": "DELIMITADO"
    }
  