from src.utils import (
    show_resized, 
    obtener_imagen_para_barcode, 
    leer_pdf417_zxing, 
    extraer_datos_cedula_pdf417, 
    leer_qr_code, 
    extraer_datos_qr,
    preprocess_for_ocr,
    ocr_mrz,
    get_mrz_candidate_lines,
    fix_common_mrz_errors,
    obtener_nombre_apellido,
    validar_mrz_tipo_documento,
    validar_mrz_pais,
    obtener_numero_identidad,
    obtener_fecha_nacimiento,
    obtener_fecha_expiracion,
    obtener_nacionalidad
)
import shutil
import pytesseract

class ValidacionCedulaService:
    """
    Servicio de validación de cédulas.
    Responsabilidad: Orquestar el proceso completo de validación.
    """

    def __init__(self):
        self.dpi_procesamiento = 300
        # Aquí podrías cargar modelos ML, configuraciones, etc.
     
    def validar_cedula(self, url_identificacion):
        """
        Procesa y valida una cédula desde un PDF.
        
        Args:
            url_identificacion: Ruta al archivo PDF
            
        Returns:
            dict: Datos extraídos y validados de la cédula
        """
        tesseract_path = shutil.which("tesseract")
        if not tesseract_path:
            raise RuntimeError(
                "❌ Tesseract no está instalado o no está en el PATH.\n"
                "Instálalo con: sudo apt install tesseract-ocr"
            )

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        original = self._obtener_imagen_para_barcode(url_identificacion)

        # show_resized("Processed", original)

        datos_finales = {}
        metodo_usado = None

        # ============================================================
        # ESTRATEGIA 1: Intentar leer PDF417 (MÁS COMÚN EN CÉDULAS)
        # ============================================================

        pdf417_data = leer_pdf417_zxing(original)
        if pdf417_data:

            print("✓ PDF417 detectado")
            info_pdf417 = extraer_datos_cedula_pdf417(pdf417_data)
        
            if info_pdf417.get("cedula") and info_pdf417.get("apellidos") and info_pdf417.get("nombres"):
                print("✓ Datos completos extraídos del PDF417")
                datos_finales = {
                    "metodo": "PDF417",
                    "cedula": info_pdf417["cedula"],
                    "apellidos": info_pdf417["apellidos"],
                    "nombres": info_pdf417["nombres"],
                    "fecha_nacimiento": info_pdf417["fecha_nacimiento"],
                    "sexo": info_pdf417["sexo"],
                    "rh": info_pdf417.get("rh"),
                }
                metodo_usado = "PDF417"
            else:
                print("⚠ PDF417 detectado pero datos incompletos")
        else:
            print("✗ No se detectó código PDF417")

        # ============================================================
        # ESTRATEGIA 2: Intentar leer QR CODE
        # ============================================================

        if not metodo_usado:
            qr_data = leer_qr_code(original)

            if qr_data:
                print("✓ QR Code detectado")
                info_qr = extraer_datos_qr(qr_data)
            
                if info_qr.get("cedula") and (info_qr.get("apellidos") or info_qr.get("nombres")):
                    print("✓ Datos extraídos del QR Code")
                    datos_finales = {
                        "metodo": "QR",
                        "cedula": info_qr["cedula"],
                        "apellidos": info_qr["apellidos"],
                        "nombres": info_qr["nombres"],
                        "fecha_nacimiento": info_qr.get("fecha_nacimiento"),
                        "sexo": info_qr.get("sexo"),
                    }
                    metodo_usado = "QR"
                else:
                    print("⚠ QR detectado pero datos incompletos")
            else:
                print("✗ No se detectó código QR")
        # ============================================================
        # ESTRATEGIA 3: FALLBACK FINAL - OCR del MRZ
        # ============================================================
        if not metodo_usado:
            print("\n" + "="*80)
            print("ESTRATEGIA 3 (FALLBACK): USANDO OCR DEL MRZ...")
            print("="*80)
            
            try:
                processed = preprocess_for_ocr(
                    original,
                    clahe_clip=1.2,
                    clahe_tile=8,
                    blur_kind="gaussian",
                    blur_ksize=5,
                    blur_sigma=0.5,
                    threshold_kind="adaptive",
                    adaptive_block=16,
                    adaptive_C=3,
                )
                # show_resized("Processed", processed)
                # processed = crop_mrz_last_quarter(processed)
                raw_text = ocr_mrz(processed)
                print(raw_text)
                mrz_lines = get_mrz_candidate_lines(raw_text)

                if len(mrz_lines) < 3:
                    raise ValueError("No se encontraron 3 líneas MRZ")

                mrz_lines[0] = fix_common_mrz_errors(mrz_lines[0])
                mrz_lines[1] = fix_common_mrz_errors(mrz_lines[1])
                mrz_lines[2] = fix_common_mrz_errors(mrz_lines[2])

                apellido, nombre = obtener_nombre_apellido(mrz_lines[2])
                
                datos_finales = {
                    "metodo": "MRZ-OCR",
                    "tipo_documento": validar_mrz_tipo_documento(mrz_lines[0]),
                    "pais": validar_mrz_pais(mrz_lines[0]),
                    "cedula": obtener_numero_identidad(mrz_lines[0]),
                    "fecha_nacimiento": obtener_fecha_nacimiento(mrz_lines[1]),
                    "sexo": mrz_lines[1][7],
                    "fecha_expiracion": obtener_fecha_expiracion(mrz_lines[1]),
                    "nacionalidad": obtener_nacionalidad(mrz_lines[1]),
                    "apellidos": apellido,
                    "nombres": nombre,
                }
                metodo_usado = "MRZ-OCR"
                print("✓ Datos extraídos del MRZ correctamente")
                
            except Exception as e:
                print(f"✗ Error al procesar MRZ: {e}")
                datos_finales = {"metodo": "ERROR", "error": str(e)}

    
        if original is not None:
            print("PAth: ", url_identificacion)
            if metodo_usado:
                return {
                    "success": True,
                    "message": f"Cédula procesada correctamente usando {metodo_usado}",
                    "data": datos_finales,
                    "urlIdentificacion": url_identificacion
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo extraer información del documento (PDF417 o QR no detectados)",
                    "data": None,
                    "urlIdentificacion": url_identificacion
                }
                
        return {
            "success": False, 
            "message": "No se pudo procesar la cédula porque no se obtuvo la imagen",
            "urlIdentificacion": url_identificacion
        }
    

    def _obtener_imagen_para_barcode(self, pdf_path):
        """Obtiene la imagen para el barcode"""
        return obtener_imagen_para_barcode(pdf_path, dpi=self.dpi_procesamiento)
    
    