"""Módulo 2 – Historial de monitoreo y visualización del Excel."""
import os

from flask import Blueprint, render_template, send_file

from app.controllers.comun import Formulario
from app.models.repositorio_monitoreo import CAMPOS_ORDENABLES
from app.services import monitoreo_service as servicio

bp = Blueprint("datos", __name__, url_prefix="/datos")


@bp.route("/")
def index():
    repo = servicio.obtener_repositorio()
    form = Formulario()
    desde = form.fecha("desde", None, "Desde", repo.inicio.date(), repo.fin.date())
    hasta = form.fecha("hasta", None, "Hasta", repo.inicio.date(), repo.fin.date())
    estado = form.opcion("estado", repo.estados(), "")
    texto = form.texto("q", 60)
    pagina = form.int("pagina", 1, "Página", 1, 10_000)
    por_pagina = form.int("por_pagina", 25, "Filas por página", 10, 100)
    orden = form.opcion("orden", list(CAMPOS_ORDENABLES), "fecha")
    direccion = form.opcion("dir", ["asc", "desc"], "asc")
    datos = servicio.historial_paginado(repo, desde, hasta, estado, texto, pagina, por_pagina,
                                        orden, direccion == "desc")
    return render_template("datos.html", datos=datos, form=form.valores, errores=form.errores,
                           estados=repo.estados(), diccionario=repo.diccionario,
                           supuestos=repo.supuestos, total_archivo=len(repo),
                           ausentes=len(repo.faltantes()))


@bp.route("/descargar")
def descargar():
    repo = servicio.obtener_repositorio()
    return send_file(repo.ruta_archivo, as_attachment=True,
                     download_name=os.path.basename(repo.ruta_archivo))
