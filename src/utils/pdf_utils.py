
from pathlib import Path

import fitz  
import numpy as np
import cv2

def pdf_to_images(pdf_path, dpi, page_numbers):
    """
    Convierte un archivo PDF en una lista de imágenes (OpenCV - BGR).

    Args:
        pdf_path (str | Path): Ruta al archivo PDF.
        dpi (int): Resolución de salida (recomendado 300 para OCR).
        page_numbers (list[int] | None): Páginas específicas a convertir (0-indexed).
                                          Si es None, convierte todas.

    Returns:
        List[np.ndarray]: Lista de imágenes en formato BGR (OpenCV).

    Raises:
        FileNotFoundError: Si el PDF no existe.
        ValueError: Si el archivo no es un PDF válido.
    """
    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"No existe el archivo PDF: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"El archivo no es un PDF válido: {pdf_path}")

    images: List[np.ndarray] = []
    with fitz.open(pdf_path) as doc:
        total_pages = doc.page_count
        pages = page_numbers if page_numbers is not None else range(total_pages)

        for page_index in pages:
            if page_index < 0 or page_index >= total_pages:
                raise IndexError(f"Página fuera de rango: {page_index}")

            page = doc.load_page(page_index)
            pix = page.get_pixmap(dpi=dpi)

            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = img[:, :, :3]

            images.append(img)

    return images