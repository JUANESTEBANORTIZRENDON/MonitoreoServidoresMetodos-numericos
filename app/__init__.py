"""Fábrica de la aplicación Flask (patrón MVC)."""
from __future__ import annotations

import logging
import math
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request

from config import Config


def _configurar_logs(app: Flask) -> None:
    os.makedirs(app.config["LOG_DIR"], exist_ok=True)
    manejador = RotatingFileHandler(os.path.join(app.config["LOG_DIR"], "app.log"),
                                    maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    manejador.setLevel(logging.INFO)
    raiz = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in raiz.handlers):
        raiz.addHandler(manejador)
    raiz.setLevel(logging.INFO)


def _filtro_f5(valor, decimales: int = 5):
    """Presentación con 5 decimales; los ausentes se muestran como «—»."""
    if valor is None:
        return "—"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return valor
    if not math.isfinite(v):
        return "—"
    return f"{v:.{decimales}f}"


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    _configurar_logs(app)
    app.jinja_env.filters["f5"] = _filtro_f5

    # Carga del Excel al iniciar. Si falla, la app arranca y muestra un error claro.
    from app.services.excel_service import ErrorDatosExcel, cargar_excel
    try:
        app.extensions["repositorio_monitoreo"] = cargar_excel(app.config["DATA_PATH"])
    except ErrorDatosExcel as exc:
        app.logger.error("No se pudieron cargar los datos: %s", exc)
        app.extensions["repositorio_monitoreo"] = None
        app.extensions["error_datos"] = str(exc)

    from app.controllers import (dashboard_controller, datos_controller, edo_controller,
                                 integracion_controller)
    for modulo in (dashboard_controller, datos_controller, integracion_controller, edo_controller):
        app.register_blueprint(modulo.bp)

    @app.before_request
    def _verificar_datos():
        if request.endpoint == "static":
            return None
        if app.extensions.get("repositorio_monitoreo") is None:
            return render_template("error.html", titulo="Datos no disponibles",
                                   mensaje=app.extensions.get("error_datos")), 503
        return None

    @app.errorhandler(404)
    def _no_encontrado(_e):
        return render_template("error.html", titulo="Página no encontrada",
                               mensaje="La dirección solicitada no existe."), 404

    @app.errorhandler(Exception)
    def _error_interno(exc):
        from werkzeug.exceptions import HTTPException
        if isinstance(exc, HTTPException):
            return exc
        app.logger.exception("Error no controlado en %s", request.path)
        return render_template("error.html", titulo="Error interno",
                               mensaje="Ocurrió un error inesperado. El detalle técnico quedó "
                                       "registrado en logs/app.log."), 500

    @app.context_processor
    def _contexto_global():
        repo = app.extensions.get("repositorio_monitoreo")
        return {"servidor_global": repo.servidor if repo else "—"}

    return app
