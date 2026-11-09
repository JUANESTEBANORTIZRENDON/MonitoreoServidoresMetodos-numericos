"""Punto de entrada WSGI para producción (Render): gunicorn wsgi:app

Se usa un archivo aparte porque «app» ya es el nombre del paquete de la aplicación,
así que «gunicorn app:app» importaría el paquete y no el archivo app.py.
"""
from app import create_app

app = create_app()
