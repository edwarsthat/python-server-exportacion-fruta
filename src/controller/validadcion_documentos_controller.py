from src.utils.pdf_utils import pdf_to_images
from src.utils.image_utils import preprocess_for_ocr
import cv2
import json

def validar_cedula(envelope):
    try:
        print(envelope)
        print(type(envelope))
        data_str = envelope.get("data")
        if not data_str:
            print("❌ No hay data en el request")
            return False
        
        data = json.loads(data_str)
        filePath = "../" + data.get("urlIdentificacion")

        print(f"📂 Intentando leer: {filePath}")

        imagen = pdf_to_images(filePath, 300, None)
        img_processed = preprocess_for_ocr(imagen[0])

        cv2.imshow("Pagina 1", img_processed)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"❌ Excepción en validar_cedula: {e}")
        return False