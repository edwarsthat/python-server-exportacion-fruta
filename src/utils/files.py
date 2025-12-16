import os
from pathlib import Path

def leer_archivo(ruta: str) -> bytes:
    try:
        path = Path(ruta)

        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {path}")

        if not path.is_file():
            raise ValueError(f"No es un archivo válido: {path}")

        with open(path, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return None