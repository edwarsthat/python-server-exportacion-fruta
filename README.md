# Python Server Exportación Fruta

Este proyecto es un servidor TCP en Python que maneja predicciones para la exportación de fruta utilizando modelos de Machine Learning.

## Configuración del Entorno de Desarrollo

### Requisitos Previos
- Python 3.10 o superior

### Instalación

1. **Crear y activar el entorno virtual:**

   El entorno ya ha sido configurado en la carpeta `venv`.
   Para activarlo manualmente:
   ```bash
   source venv/bin/activate
   ```

2. **Instalar dependencias:**

   Si necesitas reinstalar:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar el servidor:

```bash
# Asegúrate de que el entorno virtual esté activo o usa el python del venv
./venv/bin/python main.py
```

El servidor escuchará en `127.0.0.1:65432`.

## Estructura del Proyecto

- `main.py`: Punto de entrada del servidor TCP.
- `src/handlers/modelos.py`: Lógica para manejar las predicciones (Regresión Lineal).
- `ml_models/`: Contiene el modelo entrenado (`modelo_entrenado.pkl`).
- `requirements.txt`: Lista de dependencias del proyecto.
