

"""
Módulo de controladores para el servidor.
"""

from .validacion_documentos_controller import (
    ValidarDocumentosController,
    VALIDAR_DOCUMENTOS_ROUTES,
    controllerValidarDocumentos
)
from .talentoHumando.imagen_controller import (
    ProcesamientoImagenController,
    VALIDAR_DOCUMENTOS_ROUTES_TALENTO_HUMANO,
    controllerProcesamientoImagen
)

__all__ = [
    'ValidarDocumentosController',
    'VALIDAR_DOCUMENTOS_ROUTES',
    'controllerValidarDocumentos',
    'ProcesamientoImagenController',
    'VALIDAR_DOCUMENTOS_ROUTES_TALENTO_HUMANO',
    'controllerProcesamientoImagen'
]