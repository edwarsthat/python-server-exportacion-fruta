from src.routes.modelos_routes import MODELOS_ROUTES

# Aquí centralizamos todas las rutas.
# Si tienes más archivos de rutas (ej: usuarios_routes), impórtalos y súmalos.

ROUTES = {}

# Merge de diccionarios (Python 3.9+ usa |, versiones viejas usa {**x, **y})
# Usaremos .update() para máxima compatibilidad y claridad

ROUTES.update(MODELOS_ROUTES)
# ROUTES.update(USUARIOS_ROUTES)
# ROUTES.update(OTRAS_RUTAS)
