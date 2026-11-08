"""Módulo 7 – Integración numérica de la potencia (energía consumida).

Llama a: TrapecioCompuesto, Simpson13Compuesto, Simpson38Compuesto, Romberg,
tabla_comparativa.
"""
from flask import Blueprint, render_template

from app.controllers.comun import Formulario, ejecutar_seguro, grafica, serie
from app.metodos_numericos import (ErrorValidacion, Romberg, Simpson13Compuesto,
                                   Simpson38Compuesto, TrapecioCompuesto, tabla_comparativa)
from app.services import monitoreo_service as servicio

bp = Blueprint("integracion", __name__, url_prefix="/integracion")


@bp.route("/")
def index():
    repo = servicio.obtener_repositorio()
    form = Formulario()
    horas = form.int("horas", 24, "Duración (horas = subintervalos)", 1, 168)
    primero, ultimo = servicio.fechas_disponibles(repo, horas)
    fecha = form.fecha("fecha", primero, "Fecha inicial", primero, ultimo)
    ctx = {"form": form.valores, "errores": form.errores, "rango": (primero, ultimo)}
    try:
        datos = servicio.periodo(repo, fecha, horas)
        t, P = datos["t"], datos["potencia"]
        resultados = [
            ejecutar_seguro("Trapecio compuesto", lambda: TrapecioCompuesto(t, P).resolver()),
            ejecutar_seguro("Simpson 1/3 compuesto", lambda: Simpson13Compuesto(t, P).resolver()),
            ejecutar_seguro("Simpson 3/8 compuesto", lambda: Simpson38Compuesto(t, P).resolver()),
            ejecutar_seguro("Romberg", lambda: Romberg(t, P).resolver()),
        ]
        comparacion = tabla_comparativa(resultados)
        referencia = resultados[3].resultado
        for fila in comparacion:
            fila["kwh"] = fila["resultado"] / 1000.0 if fila["resultado"] is not None else None
            fila["dif_romberg"] = (abs(fila["resultado"] - referencia)
                                   if fila["resultado"] is not None and referencia is not None else None)
        ctx.update({
            "datos": datos, "horas": horas, "resultados": resultados, "comparacion": comparacion,
            "fecha_sel": fecha,
            "graf": grafica(
                "line", f"Potencia del servidor P(t) – {datos['inicio']:%Y-%m-%d %H:%M} a "
                        f"{datos['fin']:%Y-%m-%d %H:%M}",
                "Fecha y hora", "Potencia (W)",
                [serie("P(t) (W)", P, "#0d3b66", relleno=True)], labels=datos["etiquetas"]),
            "graf_comp": grafica(
                "bar", "Energía estimada por método", "Método", "Energía (Wh)",
                [serie("Energía (Wh)", [f["resultado"] for f in comparacion],
                       ["#0d3b66", "#3a86ff", "#2a9d8f", "#f4a259"])],
                labels=[f["metodo"] for f in comparacion], cero=False),
        })
    except ErrorValidacion as exc:
        form.errores.append(str(exc))
    return render_template("integracion.html", **ctx)
