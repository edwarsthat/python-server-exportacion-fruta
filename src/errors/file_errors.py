"""Excepciones personalizadas para el servicio de archivos."""


class FileServiceError(Exception):
    """Excepción base para errores del servicio de archivos."""
    pass


class FileNotFoundError(FileServiceError):
    """El archivo no existe."""
    pass


class FileAccessDeniedError(FileServiceError):
    """Acceso denegado: intento de path traversal o fuera del directorio permitido."""
    pass


class InvalidLocationError(FileServiceError):
    """La ubicación especificada no es válida."""
    pass


class InvalidPathError(FileServiceError):
    """La ruta proporcionada no es válida (vacía, caracteres inválidos, etc)."""
    pass


class DecryptionError(FileServiceError):
    """Error al desencriptar: archivo corrupto, clave incorrecta o padding inválido."""
    pass
