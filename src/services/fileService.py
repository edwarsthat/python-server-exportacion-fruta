import os
import base64
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from Crypto.Cipher import AES

from src.config.config import Config
from src.errors import (
    FileNotFoundErr,
    FileAccessDeniedError,
    InvalidLocationError,
    InvalidPathError,
    DecryptionError,
)


class ErrorType(Enum):
    """Tipos de error para ValidationResult."""
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    INVALID_LOCATION = "invalid_location"
    INVALID_PATH = "invalid_path"
    OTHER = "other"

IV_LENGTH = 12
AUTH_TAG_LENGTH = 16

# Directorio raíz de la aplicación (src/services -> raíz del proyecto)
APP_ROOT = Path(__file__).resolve().parent.parent.parent

# El almacenamiento está una carpeta arriba de la raíz de la app
STORAGE_BASE = APP_ROOT.parent / 'storage'

STORAGE_LOCATIONS = {
    'STORAGE': STORAGE_BASE,
    'TEMPLATES': STORAGE_BASE / 'templates',
    'PUBLIC': STORAGE_BASE / 'public',
    'UPLOADS': STORAGE_BASE / 'uploads',
}


@dataclass
class ValidationResult:
    is_valid: bool
    resolved_path: Optional[Path]
    error: Optional[str]
    error_type: Optional[ErrorType] = None


class FileService:
    """Servicio para lectura segura de archivos con protección contra Path Traversal."""

    @classmethod
    def _raise_validation_error(cls, validation: ValidationResult):
        """Lanza la excepción apropiada según el tipo de error."""
        error_map = {
            ErrorType.NOT_FOUND: FileNotFoundErr,
            ErrorType.ACCESS_DENIED: FileAccessDeniedError,
            ErrorType.INVALID_LOCATION: InvalidLocationError,
            ErrorType.INVALID_PATH: InvalidPathError,
        }
        exception_class = error_map.get(validation.error_type, FileAccessDeniedError)
        raise exception_class(validation.error)

    @classmethod
    def validate_file_path(cls, file_path: str, allowed_location: str = 'STORAGE') -> ValidationResult:
        """
        Valida una ruta de archivo contra Path Traversal.
        """
        try:
            if not file_path:
                return ValidationResult(
                    False, None, 'Ruta de archivo no proporcionada', ErrorType.INVALID_PATH
                )

            base_dir = STORAGE_LOCATIONS.get(allowed_location)
            if not base_dir:
                return ValidationResult(
                    False, None,
                    f"Ubicación no válida: {allowed_location}. Permitidas: {', '.join(STORAGE_LOCATIONS.keys())}",
                    ErrorType.INVALID_LOCATION
                )

            # Limpiar caracteres nulos y resolver ruta
            sanitized_path = file_path.replace('\0', '')
            resolved_path = (base_dir / sanitized_path).resolve()

            # Protección contra Path Traversal
            try:
                resolved_path.relative_to(base_dir)
            except ValueError:
                return ValidationResult(
                    False, None, 'Acceso denegado: fuera del directorio permitido', ErrorType.ACCESS_DENIED
                )

            if not resolved_path.exists():
                return ValidationResult(False, None, 'Archivo no encontrado', ErrorType.NOT_FOUND)

            if not resolved_path.is_file():
                return ValidationResult(
                    False, None, 'La ruta no pertenece a un archivo válido', ErrorType.INVALID_PATH
                )

            return ValidationResult(True, resolved_path, None, None)

        except Exception as e:
            return ValidationResult(False, None, f'Error de acceso: {str(e)}', ErrorType.OTHER)

    @classmethod
    def read_file(cls, file_path: str, location: str = 'STORAGE', decrypt: bool = False) -> bytes:
        """Lee un archivo como bytes, opcionalmente desencriptándolo."""
        validation = cls.validate_file_path(file_path, location)

        if not validation.is_valid:
            cls._raise_validation_error(validation)

        buffer = validation.resolved_path.read_bytes()

        if decrypt:
            return cls.decrypt_buffer(buffer)

        return buffer

    @classmethod
    def read_template(cls, template_sub_path: str) -> str:
        """Lee un archivo de template como texto UTF-8."""
        validation = cls.validate_file_path(template_sub_path, 'TEMPLATES')

        if not validation.is_valid:
            cls._raise_validation_error(validation)

        return validation.resolved_path.read_text(encoding='utf-8')

    @classmethod
    def read_file_as_base64(cls, file_path: str, location: str = 'STORAGE') -> str:
        """Lee un archivo y lo retorna como data URI en base64."""
        validation = cls.validate_file_path(file_path, location)

        if not validation.is_valid:
            cls._raise_validation_error(validation)

        buffer = validation.resolved_path.read_bytes()
        ext = validation.resolved_path.suffix.lower()

        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
        }
        mime = mime_map.get(ext, 'application/octet-stream')

        encoded = base64.b64encode(buffer).decode('utf-8')
        return f"data:{mime};base64,{encoded}"

    @classmethod
    def get_file_stats(cls, file_path: str, location: str = 'STORAGE') -> os.stat_result:
        """Obtiene las estadísticas de un archivo."""
        validation = cls.validate_file_path(file_path, location)

        if not validation.is_valid:
            cls._raise_validation_error(validation)

        return validation.resolved_path.stat()

    @classmethod
    def get_template_dir(cls, template_sub_path: str) -> Path:
        """Obtiene el directorio de un template."""
        validation = cls.validate_file_path(template_sub_path, 'TEMPLATES')

        if not validation.is_valid:
            cls._raise_validation_error(validation)

        return validation.resolved_path.parent

    @classmethod
    def decrypt_buffer(cls, encrypted_buffer: bytes) -> bytes:
        """Desencripta un buffer encriptado con AES-256-GCM."""
        if len(encrypted_buffer) < IV_LENGTH + AUTH_TAG_LENGTH:
            raise DecryptionError("Buffer encriptado demasiado corto")

        try:
            # Extraer IV (12 bytes)
            iv = encrypted_buffer[:IV_LENGTH]
            # Extraer auth tag (16 bytes)
            auth_tag = encrypted_buffer[IV_LENGTH:IV_LENGTH + AUTH_TAG_LENGTH]
            # Extraer contenido encriptado
            encrypted_content = encrypted_buffer[IV_LENGTH + AUTH_TAG_LENGTH:]

            cipher = AES.new(Config.ENCRYPTION_KEY, AES.MODE_GCM, iv)
            
            # Desencriptar y verificar integridad con el auth_tag
            decrypted = cipher.decrypt_and_verify(encrypted_content, auth_tag)
            
            return decrypted

        except (ValueError, KeyError) as e:
            # KeyError se lanza si la verificación del tag falla
            raise DecryptionError(f"Error de autenticación: el archivo está corrupto o la clave es incorrecta. {str(e)}")
        except Exception as e:
            raise DecryptionError(f"Error inesperado al desencriptar: {str(e)}")
