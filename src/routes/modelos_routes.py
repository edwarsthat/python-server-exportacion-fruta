from src.controller.validadcion_documentos_controller import validar_cedula

# Definimos las rutas específicas para este módulo
# Clave: Nombre de la acción (action)
# Valor: Función del controlador
MODELOS_ROUTES = {
    "post_talentoHumano_personal_ingresoPersonal": validar_cedula,
}
