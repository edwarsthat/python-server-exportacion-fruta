from src.controller import VALIDAR_DOCUMENTOS_ROUTES
from src.controller.talentoHumando.imagen_controller import VALIDAR_DOCUMENTOS_ROUTES_TALENTO_HUMANO
# Combinamos rutas
MODELOS_ROUTES = {
    **VALIDAR_DOCUMENTOS_ROUTES,
    **VALIDAR_DOCUMENTOS_ROUTES_TALENTO_HUMANO,
}
