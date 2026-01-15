from src.services.validar_cedula_service import ValidacionCedulaService

class ValidarDocumentosController:
    """
    Controlador para endpoints de validación de documentos.
    Responsabilidad: Recibir requests, validar entrada, devolver respuestas.
    """

    def __init__(self):
        self.validacion_service = ValidacionCedulaService()
    
    def validar_cedula(self, *args, **envelope):
        """
        Endpoint para validar cédula desde PDF.
        
        Args:
            *args: Puede recibir el url_identificacion como primer argumento posicional.
            **envelope: Data y urlIdentificacion pasados como keywords.
            
        Returns:
            dict: Respuesta con resultado de validación
        """
        try:
            # 1. Intentamos obtener la ruta del PDF
            # Puede venir como primer argumento posicional, o en 'urlIdentificacion', o en 'data'
            url_identificacion = None
            
            if args:
                url_identificacion = args[0]
            
            if not url_identificacion:
                url_identificacion = envelope.get("data")

            if not url_identificacion:
                print("❌ No se encontró la ruta del PDF (urlIdentificacion o data)")
                return {"success": False, "error": "Ruta de archivo no proporcionada"}

            # Limpiar posibles comillas extra si vienen en el string
            if isinstance(url_identificacion, str):
                url_identificacion = url_identificacion.strip('"').strip("'")

            print(f"📂 Intentando leer: {url_identificacion}")
            return self.validacion_service.validar_cedula(url_identificacion)
            
        except Exception as e:
            print(f"❌ Excepción en validar_cedula: {e}")
            return {"success": False, "error": str(e)}


# ✅ Instanciamos el controller UNA SOLA VEZ
controllerValidarDocumentos = ValidarDocumentosController()

# Definimos las rutas apuntando al método del controller
VALIDAR_DOCUMENTOS_ROUTES = {
    "validar_cedula": controllerValidarDocumentos.validar_cedula,
}