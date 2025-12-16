import cv2
import numpy as np


def preprocess_for_ocr(
    image,
    apply_blur= True,
    apply_threshold = True
):
    """
    Preprocesa una imagen para OCR:
    - Escala de grises
    - Aumento de contraste
    - Reducción de ruido
    - Binarización

    Args:
        image (np.ndarray): Imagen en formato BGR (OpenCV).
        apply_blur (bool): Aplica blur para reducir ruido.
        apply_threshold (bool): Aplica binarización.

    Returns:
        np.ndarray: Imagen preprocesada (lista para OCR).
    """

    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Imagen inválida para preprocesamiento")

    # 1️⃣ Escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2️⃣ Aumento de contraste (CLAHE)
    clahe = cv2.createCLAHE(
        clipLimit=1.2,
        tileGridSize=(8, 8)
    )
    contrast = clahe.apply(gray)

    # 3️⃣ Reducción de ruido
    if apply_blur:
        contrast = cv2.GaussianBlur(contrast, (3, 3), 0)

    # 4️⃣ Binarización
    if apply_threshold:
        _, binary = cv2.threshold(
            contrast,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary

    return contrast
