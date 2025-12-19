"""
Módulo de utilidades para procesamiento de documentos.
"""
from .document_processing import (
    pdf_to_images, 
    obtener_imagen_para_barcode, 
    leer_pdf417_zxing, 
    extraer_datos_cedula_pdf417,
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
from .documento_view import show_resized
from .procesar_qr import leer_qr_code, extraer_datos_qr

__all__ = [
    'pdf_to_images', 
    'show_resized',
    'obtener_imagen_para_barcode', 
    'leer_pdf417_zxing', 
    'extraer_datos_cedula_pdf417', 
    'leer_qr_code', 
    'extraer_datos_qr',
    'preprocess_for_ocr',
    'ocr_mrz',
    'get_mrz_candidate_lines',
    'fix_common_mrz_errors',
    'obtener_nombre_apellido',
    'validar_mrz_tipo_documento',
    'validar_mrz_pais',
    'obtener_numero_identidad',
    'obtener_fecha_nacimiento',
    'obtener_fecha_expiracion',
    'obtener_nacionalidad'
]