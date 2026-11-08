"""Configuración de la aplicación."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "monitor-numerico-academico")
    DATA_PATH = os.environ.get(
        "MONITOR_DATA_PATH",
        os.path.join(BASE_DIR, "data", "Historial_Monitoreo_Servidor_3_Meses.xlsx"),
    )
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    JSON_AS_ASCII = False


class TestingConfig(Config):
    TESTING = True
