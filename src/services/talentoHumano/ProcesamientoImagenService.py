import os
from src.utils.talentoHumano.carnets import procesar_foto_carnet
from src.services.fileService import FileService, STORAGE_LOCATIONS


class ProcesamientoImagenService:
    """
    Servicio de procesamiento de imágenes.
    Responsabilidad: Procesar imágenes para usar en documentos o llevar documentacion.
    """

    def __init__(self):
        self.ancho_cm = 3.11
        self.alto_cm = 3.11
        self.dpi = 300
        self.zoom_cara = 2

    def procesar_foto_carnet_service(self, url_img: str):
        try:
            # Limpiar comillas si vienen
            if isinstance(url_img, str):
                url_img = url_img.strip('"').strip("'")

            if not url_img:
                print("❌ URL de imagen vacía")
                return {"success": False, "error": "Ruta de archivo no proporcionada"}

            # Detectar si está encriptado
            is_encrypted = url_img.endswith('.enc')

            # Leer imagen con FileService (valida path traversal + desencripta si es necesario)
            imagen_bytes = FileService.read_file(url_img, location='STORAGE', decrypt=is_encrypted)

            # Definir carpeta de salida usando STORAGE_LOCATIONS
            output_dir = STORAGE_LOCATIONS['STORAGE'] / "personal" / "fotoCarnetProcessed"

            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # Generar nombre de archivo de salida
            filename = os.path.basename(url_img)
            # Remover .enc si existe para obtener el nombre base
            if filename.endswith('.enc'):
                filename = filename[:-4]
            name, ext = os.path.splitext(filename)

            # Ruta relativa (para guardar en DB)
            relative_path = f"personal/fotoCarnetProcessed/{name}_processed{ext}"
            # Ruta absoluta (para guardar el archivo)
            absolute_path = str(output_dir / f"{name}_processed{ext}")

            print(f"🖼️ Procesando carnet desde: {url_img}")
            print(f"💾 Guardando en: {absolute_path}")

            result_path = procesar_foto_carnet(
                imagen_bytes,
                output_path=absolute_path,
                ancho_cm=self.ancho_cm,
                alto_cm=self.alto_cm,
                dpi=self.dpi,
                zoom_cara=self.zoom_cara
            )

            if result_path is not None:
                return {
                    "success": True,
                    "message": "Imagen procesada correctamente",
                    "path": relative_path,
                    "original_path": url_img
                }
            else:
                return {"success": False, "error": "No se pudo generar la imagen (falló detección de cara o lectura)"}

        except Exception as e:
            print(f"Error al procesar la foto del carnet: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
