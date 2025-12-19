

"""
Módulo de controladores para el servidor.
"""

from .validacion_documentos_controller import (
    ValidarDocumentosController,
    VALIDAR_DOCUMENTOS_ROUTES,
    controller
)

__all__ = [
    'ValidarDocumentosController',
    'VALIDAR_DOCUMENTOS_ROUTES',
    'controller'
]