import cv2
import mediapipe as mp
import numpy as np

def procesar_foto_carnet( imagen_path, output_path=None, 
                             ancho_cm=3.11, alto_cm=3.11, dpi=300, 
                             zoom_cara=1.8):
    """
    Convierte una foto a formato carnet centrado.
        
    Args:
            imagen_path: ruta de la imagen de entrada
            output_path: ruta para guardar (opcional)
            ancho_cm: ancho final en centímetros
            alto_cm: alto final en centímetros
            dpi: resolución en puntos por pulgada (300 para impresión de calidad)
            zoom_cara: factor de zoom (menor = cara más grande)
                       1.5 = muy cerca, 1.8 = cerca, 2.2 = normal, 2.8 = lejos
        
    Returns:
            imagen procesada en formato carnet
        """
    try:
        # Convertir cm a píxeles
        mp_face_detection = mp.solutions.face_detection
        ancho_carnet = int(ancho_cm / 2.54 * dpi)
        alto_carnet = int(alto_cm / 2.54 * dpi)
        
        # Leer imagen
        img = cv2.imread(imagen_path)
        if img is None:
            raise ValueError(f"No se pudo leer la imagen: {imagen_path}")
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
            
        # Inicializar detector de caras dentro de la función (Context Manager)
        # Esto responde a tu pregunta: Sí, es mejor aquí para que la función sea autónoma.
        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            # Detectar cara
            results = face_detection.process(img_rgb)
                
            if not results.detections:
                raise ValueError("No se detectó ninguna cara en la imagen")
                
            # Tomar la primera cara detectada
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
                
            # Convertir coordenadas relativas a píxeles
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            ancho_cara = int(bbox.width * w)
            alto_cara = int(bbox.height * h)
                
            # Calcular centro de la cara
            centro_x = x + ancho_cara // 2
            centro_y = y + alto_cara // 2
                
            # Definir dimensiones del recorte para foto carnet cuadrada
            # Como es cuadrado, usar el mismo tamaño para ancho y alto
            tamaño_recorte = int(max(ancho_cara, alto_cara) * zoom_cara)
                
            # Calcular coordenadas del recorte
            # Para foto carnet cuadrada, centrar más la cara verticalmente
            x1 = max(0, centro_x - tamaño_recorte // 2)
            y1 = max(0, centro_y - int(tamaño_recorte * 0.55))  # 55% arriba, 45% abajo
            x2 = min(w, x1 + tamaño_recorte)
            y2 = min(h, y1 + tamaño_recorte)
                
            # Ajustar si se sale de los bordes
            if x2 - x1 < tamaño_recorte:
                if x1 == 0:
                    x2 = min(w, tamaño_recorte)
                else:
                    x1 = max(0, w - tamaño_recorte)
                
            if y2 - y1 < tamaño_recorte:
                if y1 == 0:
                    y2 = min(h, tamaño_recorte)
                else:
                    y1 = max(0, h - tamaño_recorte)
                
            # Recortar imagen
            img_recortada = img[y1:y2, x1:x2]
                
            # Redimensionar a tamaño carnet estándar
            img_carnet = cv2.resize(img_recortada, (ancho_carnet, alto_carnet), interpolation=cv2.INTER_LANCZOS4)
                
            # Guardar si se especifica ruta
            if output_path:
                cv2.imwrite(output_path, img_carnet, [cv2.IMWRITE_JPEG_QUALITY, 95])
                print(f"Foto carnet guardada en: {output_path}")

            return output_path

    except Exception as e:
        print(f"Error al procesar la foto carnet: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    
