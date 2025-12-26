import cv2
import mediapipe as mp
import numpy as np
from src.utils.talentoHumano.carnets import procesar_foto_carnet
import os

class ProcesamientoImagenService:
    """
    Servicio de procesamiento de imágenes.
    Responsabilidad: Procesar imágenes para usar en documentos o llevar documentacion.
    """
    def __init__(self):
        # Configuraciones se podrían cargar de entorno si fuera necesario
        self.ancho_cm = 3.11
        self.alto_cm = 3.11
        self.dpi = 300
        self.zoom_cara = 2
    
    def procesar_foto_carnet_service(self, url_img):
        try:
            # Limpiar comillas si vienen
            if isinstance(url_img, str):
                url_img = url_img.strip('"').strip("'")

            if not url_img or not os.path.exists(url_img):
                 print(f"❌ No existe archivo o url vacía: {url_img}")
                 return {"success": False, "error": f"Archivo no encontrado: {url_img}"}

            # Definir carpeta de salida
            # Subimos 3 niveles desde src/services/talentoHumano para llegar a la raíz del server python
            # Y luego ajustamos para salir a la carpeta de uploads general del sistema
            # Asumiendo estructura: /home/analista/server/python-server... y /home/analista/server/uploads
            
            # Obtener la raíz del proyecto actual
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            # Esto nos lleva a /home/analista/server/python-server-exportacion-fruta
            
            # Subir un nivel más para llegar a /home/analista/server
            server_root = os.path.dirname(base_dir)
            
            output_dir = os.path.join(server_root, "uploads", "personal", "fotoCarnetProcessed")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            filename = os.path.basename(url_img)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_processed{ext}")

            print(f"🖼️ Procesando carnet desde: {url_img}")
            print(f"💾 Guardando en: {output_path}")
            
            img_carnet = procesar_foto_carnet(
                url_img,
                output_path=output_path,
                ancho_cm = self.ancho_cm,
                alto_cm = self.alto_cm,
                dpi = self.dpi,
                zoom_cara = self.zoom_cara 
            )
            
            if img_carnet is not None:
                return {
                    "success": True, 
                    "message": "Imagen procesada correctamente",
                    "path": output_path,
                    "original_path": url_img
                }
            else:
                 return {"success": False, "error": "No se pudo generar la imagen (falló detección de cara o lectura)"}
        
        except Exception as e:
            print(f"Error al procesar la foto del carnet: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
