import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    _raw_key = os.environ.get('ENCRYPTION_KEY', '')
    
    try:
        # Intentar tratar como hex si tiene la longitud correcta
        if len(_raw_key) == 64:
            ENCRYPTION_KEY = bytes.fromhex(_raw_key)
        else:
            ENCRYPTION_KEY = _raw_key.encode()
    except ValueError:
        ENCRYPTION_KEY = _raw_key.encode()

    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    UPLOAD_PATH = os.environ.get('UPLOAD_PATH', './uploads')
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 65432))
    
    @staticmethod
    def validate():
        """Valida que todas las variables necesarias estén configuradas"""
        if not os.environ.get('ENCRYPTION_KEY'):
            raise ValueError("ENCRYPTION_KEY no está configurada en el archivo .env")
        
        # Validar que la clave tenga un tamaño válido para AES (16, 24 o 32 bytes)
        key_len = len(Config.ENCRYPTION_KEY)
        if key_len not in [16, 24, 32]:
            raise ValueError(
                f"La ENCRYPTION_KEY tiene un tamaño inválido ({key_len} bytes). "
                "Debe ser de 16, 24 o 32 bytes. "
                "Si es Hexadecimal, debe tener 32, 48 o 64 caracteres."
            )

# Validar al inicio
Config.validate()