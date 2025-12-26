from src.services.talentoHumano.ProcesamientoImagenService import ProcesamientoImagenService

class ProcesamientoImagenController:
    """
    Controlador para endpoints de validación de documentos.
    Responsabilidad: Recibir requests, validar entrada, devolver respuestas.
    """

    def __init__(self):
        self.procesamiento_imagen_service = ProcesamientoImagenService()
    
    def procesamiento_imagen(self, *args, **envelope):
        """
        Endpoint recibir la imagen y procesarla.
        """
        try:
            # Obtener path de la imagen
            # Puede venir como argumento posicional (si data es string) o en kwargs
            url_imagen = args[0] if args else envelope.get("urlImagen") or envelope.get("data")
            
            if not url_imagen:
                return {"success": False, "error": "Falta la ruta de la imagen (parametro 'data')"}
            
            # Llamar al servicio
            return self.procesamiento_imagen_service.procesar_foto_carnet_service(url_imagen)

        except Exception as e:
            print(f"❌ Error en controller procesamiento_imagen: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    


# ✅ Instanciamos el controller UNA SOLA VEZ
controllerProcesamientoImagen = ProcesamientoImagenController()

# Definimos las rutas apuntando al método del controller
VALIDAR_DOCUMENTOS_ROUTES_TALENTO_HUMANO = {
    "talentoHumano_procesamiento_imagen": controllerProcesamientoImagen.procesamiento_imagen,
}