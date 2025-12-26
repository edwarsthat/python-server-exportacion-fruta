import fitz
from pathlib import Path
from typing import List
import numpy as np
import cv2
import zxingcpp
import re
import pytesseract
from Crypto.Cipher import AES
import os
import tempfile
from src.config import Config

IV_LENGTH = 16

def pdf_to_images(pdf_path, dpi, page_numbers=None, max_pages=None):

    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"No existe el archivo PDF: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"El archivo no es un PDF válido: {pdf_path}")

    images: List[np.ndarray] = []
    with fitz.open(pdf_path) as doc:
        total_pages = doc.page_count
        
        if page_numbers is not None:
            pages = page_numbers
        else:
            limit = total_pages
            if max_pages is not None:
                limit = min(total_pages, max_pages)
            pages = range(limit)

        for page_index in pages:
            if page_index < 0 or page_index >= total_pages:
                continue # Skip invalid pages instead of crashing, or crash if strictly required. Keeping original intent but safer? No, original raised.
                # raise IndexError(f"Página fuera de rango: {page_index}") 
                # Original raised, let's keep raising if explicitly requested, but for range it won't happen.

            page = doc.load_page(page_index)
            pix = page.get_pixmap(dpi=dpi)

            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = img[:, :, :3]

            images.append(img)

    return images

def crop_mrz_last_quarter(img, ratio=0.65):
    """
    Recorta el último cuarto (o porcentaje configurable) de la imagen.
    ratio=0.75 -> último 25%
    ratio=0.65 -> último 35%
    """
    h, w = img.shape[:2]
    y0 = int(h * ratio)
    return img[y0:h, 0:w]

def decrypt_file(encrypted_file_path):
    """
    Desencripta un archivo y retorna los bytes desencriptados
    """
    with open(encrypted_file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Extrae IV (primeros 16 bytes)
    iv = encrypted_data[:IV_LENGTH]
    encrypted_content = encrypted_data[IV_LENGTH:]
    
    # Desencripta
    cipher = AES.new(Config.ENCRYPTION_KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_content)
    
    # Remueve padding PKCS7
    padding_length = decrypted[-1]
    return decrypted[:-padding_length]

def obtener_imagen_para_barcode(pdf_path, dpi=300):
    """
    Devuelve una imagen (np.ndarray BGR) adecuada para detectar PDF417:
    - Si el PDF tiene 2+ páginas: usa la segunda página completa
    - Si el PDF tiene 1 página: recorta la mitad inferior
    
    Soporta archivos encriptados (con extensión .enc)
    """
    
    # Verificar si el archivo está encriptado
    is_encrypted = pdf_path.endswith('.enc')
    
    if is_encrypted:
        # Desencriptar el archivo
        decrypted_data = decrypt_file(pdf_path)
        
        # Crear archivo temporal con los datos desencriptados
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(decrypted_data)
            temp_pdf_path = temp_file.name
        
        try:
            # Procesar el archivo temporal desencriptado
            # Solo necesitamos las primeras 2 páginas máximo para decidir
            print("Procesando archivo temporal desencriptado...")
            images = pdf_to_images(temp_pdf_path, dpi=dpi, page_numbers=None, max_pages=2)
        finally:
            # Eliminar archivo temporal
            os.unlink(temp_pdf_path)
    else:
        # Archivo no encriptado, procesar normalmente
        # Solo necesitamos las primeras 2 páginas máximo
        print("Procesando archivo no encriptado...")
        images = pdf_to_images(pdf_path, dpi=dpi, page_numbers=None, max_pages=2)

    if not images:
        raise ValueError("No se pudieron extraer imágenes del PDF")

    # Elegir imagen base
    if len(images) >= 2:
        img = images[1]  # segunda página (índice 1)
    else:
        img = images[0]  # única página
        
        # Recortar mitad inferior
        h, w = img.shape[:2]
        img = img[int(h * 0.5):h, 0:w]

    return img

def leer_pdf417_zxing(img):
    if not isinstance(img, np.ndarray):
        img = np.array(img)

    if img.dtype != np.uint8:
        img = img.astype(np.uint8)

    if img.ndim == 3:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img

    results = zxingcpp.read_barcodes(img_rgb)

    print("ZXing encontró:", len(results))
    for r in results:
        print("Formato:", r.format.name, "len:", len(r.text))

    for r in results:
        if r.format.name == "PDF417" and r.text:
            return r.text

    return None

def extraer_datos_cedula_pdf417(raw):
    
    # Reemplazar <NUL> y caracteres nulos reales por pipe
    s = raw.replace("<NUL>", "|").replace("\x00", "|")
    
    # Limpiar pipes múltiples
    s = re.sub(r"\|+", "|", s)
    
    # Dividir por pipes
    parts = [p.strip() for p in s.split("|") if p.strip()]

    # 1) Cédula: primer número de 8-10 dígitos
    cedula = next((p for p in parts if re.fullmatch(r"\d{8,10}", p)), None)
    
    # 2) Buscar palabras que sean SOLO letras mayúsculas (apellidos y nombres)
    letras = [p for p in parts if re.fullmatch(r"[A-ZÁÉÍÓÚÑ]+", p) and len(p) >= 3]
    
    apellidos = None
    nombres = None
    
    if len(letras) >= 3:
        # Típicamente: APELLIDO1, APELLIDO2, NOMBRE(S)
        apellidos = f"{letras[0]} {letras[1]}"
        nombres = " ".join(letras[2:])
    elif len(letras) == 2:
        apellidos = letras[0]
        nombres = letras[1]
    elif len(letras) == 1:
        apellidos = letras[0]

    
    # 3) Sexo y fecha de nacimiento
    sexo = None
    fecha_nacimiento = None
    
    # Buscar en todo el string el patrón 0M/1F seguido de fecha
    sexo_fecha_match = re.search(r"[01]([MF])(\d{8})", raw)
    if sexo_fecha_match:
        sexo = sexo_fecha_match.group(1)
        fecha_nacimiento = sexo_fecha_match.group(2)
    
    
    # 4) RH
    rh = None
    rh_match = re.search(r"(AB|A|B|O)[+-]", raw)
    if rh_match:
        rh = rh_match.group(0)
        
    return {
        "cedula": cedula,
        "apellidos": apellidos,
        "nombres": nombres,
        "fecha_nacimiento": fecha_nacimiento,
        "sexo": sexo,
        "rh": rh,
    }

def preprocess_for_ocr(
    image: np.ndarray,
    clahe_clip: float = 0.6,
    clahe_tile: int = 16,
    blur_kind: str = "gaussian",
    blur_ksize: int = 3,
    blur_sigma: float = 0.5,
    threshold_kind: str = "otsu",
    adaptive_block: int = 31,
    adaptive_C: int = 10,
):
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Imagen inválida para preprocesamiento")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(
        clipLimit=float(clahe_clip),
        tileGridSize=(int(clahe_tile), int(clahe_tile))
    )
    proc = clahe.apply(gray)

    # Blur (opcional)
    if blur_kind == "gaussian":
        k = int(blur_ksize)
        if k % 2 == 0:
            k += 1
        proc = cv2.GaussianBlur(proc, (k, k), float(blur_sigma))
    elif blur_kind == "median":
        k = int(blur_ksize)
        if k % 2 == 0:
            k += 1
        proc = cv2.medianBlur(proc, k)
    elif blur_kind == "none":
        pass
    else:
        raise ValueError(f"blur_kind inválido: {blur_kind}")

    # Threshold (opcional)
    if threshold_kind == "otsu":
        _, proc = cv2.threshold(proc, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif threshold_kind == "adaptive":
        b = int(adaptive_block)
        if b % 2 == 0:
            b += 1
        proc = cv2.adaptiveThreshold(
            proc, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            b,
            int(adaptive_C)
        )
    elif threshold_kind == "none":
        pass
    else:
        raise ValueError(f"threshold_kind inválido: {threshold_kind}")

    return proc

def ocr_mrz(img):
    config = (
        "--oem 3 --psm 6 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    )
    return pytesseract.image_to_string(img, lang="eng", config=config)

def get_mrz_candidate_lines(text):
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if len(ln) >= 20 and "<" in ln:
            lines.append(ln)
    return lines

def fix_common_mrz_errors(line):
    # Traducir errores comunes de OCR en MRZ
    replacements = {'(': '<', ')': '<', '{': '<', '}': '<', '[': '<', ']': '<'}
    for k, v in replacements.items():
        line = line.replace(k, v)
    return re.sub(r'[^A-Z0-9<]', '', line.upper())

def obtener_nombre_apellido(line):
    parts = line.split('<<')
    apellido = parts[0].replace('<', ' ').strip() if len(parts) > 0 else ""
    nombre = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    return apellido, nombre

def validar_mrz_tipo_documento(line):
    if not line:
        return "Error"
    
    first_char = line[0].upper()
    
    if first_char == 'I':
        return "Identificación"
    elif first_char == 'P':
        return "Pasaporte"
    else:
        return "Error"

def validar_mrz_pais(line):
    return line[2:5].replace('<', '').strip()

def obtener_numero_identidad(line):
    return line[5:14].replace('<', '').strip()

def obtener_fecha_nacimiento(line):
    return line[0:6]

def obtener_fecha_expiracion(line):
    return line[8:14]

def obtener_nacionalidad(line):
    return line[15:18].replace('<', '').strip()

