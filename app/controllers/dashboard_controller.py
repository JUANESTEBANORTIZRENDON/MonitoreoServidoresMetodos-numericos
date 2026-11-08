"""Módulo 1 – Dashboard."""
from flask import Blueprint, render_template

from app.controllers.comun import Formulario, grafica, serie
from app.metodos_numericos import ErrorValidacion
from app.services import monitoreo_service as servicio

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    repo = servicio.obtener_repositorio()
    form = Formulario()
    desde = form.fecha("desde", repo.inicio.date(), "Desde", repo.inicio.date(), repo.fin.date())
    hasta = form.fecha("hasta", repo.fin.date(), "Hasta", repo.inicio.date(), repo.fin.date())
    estado = form.opcion("estado", repo.estados(), "")
    if desde and hasta and desde > hasta:
        form.errores.append("La fecha «Desde» debe ser anterior o igual a «Hasta».")
        desde, hasta = repo.inicio.date(), repo.fin.date()
    resumen, graf = None, None
    try:
        resumen = servicio.resumen_dashboard(repo, desde, hasta, estado)
        g = resumen["grafica"]
        graf = grafica("line", f"Temperatura del servidor y uso de CPU – {resumen['servidor']}",
                       "Fecha y hora", "Temperatura (°C)",
                       [serie("Temp. servidor (°C)", g["temperatura"], "#0d3b66", eje="y"),
                        serie("CPU (%)", g["cpu"], "#f4a259", eje="y2")],
                       labels=g["labels"], y2_titulo="CPU (%)", lineas_umbral=[70, 80])
    except ErrorValidacion as exc:
        form.errores.append(str(exc))
    return render_template("dashboard.html", resumen=resumen, grafica=graf, form=form.valores,
                           errores=form.errores, estados=repo.estados(),
                           rango=(repo.inicio.date(), repo.fin.date()))
