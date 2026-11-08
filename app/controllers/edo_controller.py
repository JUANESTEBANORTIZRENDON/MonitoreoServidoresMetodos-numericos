"""Módulo 8 – Ecuaciones diferenciales ordinarias (modelo térmico).

Llama a: ModeloTermicoEDO, alfa_estado_estacionario, Euler, Heun, Ralston, RungeKutta4,
errores_serie, tabla_comparativa.
"""
import math

from flask import Blueprint, render_template

from app.controllers.comun import Formulario, ejecutar_seguro, grafica, serie
from app.metodos_numericos import (ErrorValidacion, Euler, Heun, ModeloTermicoEDO, Ralston,
                                   RungeKutta4, errores_serie, tabla_comparativa)
from app.metodos_numericos.edo import alfa_estado_estacionario
from app.services import monitoreo_service as servicio

bp = Blueprint("edo", __name__, url_prefix="/edo")

CLASES = (Euler, Heun, Ralston, RungeKutta4)
COLORES = ["#e76f51", "#3a86ff", "#2a9d8f", "#f4a259"]


@bp.route("/")
def index():
    repo = servicio.obtener_repositorio()
    form = Formulario()
    horas = form.int("horas", 24, "Duración (h)", 1, 168)
    primero, ultimo = servicio.fechas_disponibles(repo, horas)
    fecha = form.fecha("fecha", primero, "Fecha inicial", primero, ultimo)
    beta = form.float("beta", 0.35, "β (h⁻¹)", 1e-6, 10)
    P_idle = form.float("P_idle", 150.0, "P_idle (W)", 0, 2000)
    h = form.float("h", 1.0, "Paso h (h)", 0.05, 24)
    ctx = {"form": form.valores, "errores": form.errores, "rango": (primero, ultimo)}
    try:
        datos = servicio.periodo(repo, fecha, horas)
        temps = datos["temp_servidor"]
        alfa_sug = alfa_estado_estacionario(beta, P_idle, datos["potencia"], list(temps),
                                            datos["temp_entrada"])
        alfa = form.float("alfa", 0.045, "α (°C/(h·W))", -10, 10)
        n_pasos = horas / h
        if abs(n_pasos - round(n_pasos)) > 1e-9:
            raise ErrorValidacion(f"La duración ({horas} h) debe ser múltiplo del paso h = {h}.")
        n_pasos = int(round(n_pasos))
        if n_pasos > 5000:
            raise ErrorValidacion("Demasiados pasos: aumente h o reduzca la duración.")
        idx0 = next((i for i, v in enumerate(temps) if not math.isnan(v)), None)
        if idx0 is None:
            raise ErrorValidacion("El periodo no tiene temperaturas válidas.")
        t0 = datos["t"][idx0]
        T0 = float(temps[idx0])
        pasos = int(round((horas - t0) / h))
        modelo = ModeloTermicoEDO(alfa, beta, P_idle, datos["t"], datos["potencia"],
                                  datos["temp_entrada"])
        modelo.validar()
        resultados = [ejecutar_seguro(c.nombre, lambda c=c: c(modelo.f, t0, T0, h, pasos).resolver())
                      for c in CLASES]

        # Comparación con el historial en los instantes que coinciden con una hora exacta
        observados_por_t = {round(t, 9): v for t, v in zip(datos["t"], temps)}
        comparacion = tabla_comparativa(resultados)
        for fila, r in zip(comparacion, resultados):
            if not r.iteraciones:
                fila.update({"error_promedio": None, "error_maximo": None, "n": 0})
                continue
            obs, sim = [], []
            for paso in r.iteraciones:
                v = observados_por_t.get(round(paso["t"], 9))
                if v is not None:
                    obs.append(v)
                    sim.append(paso["y"])
            try:
                e = errores_serie(obs, sim)
            except ErrorValidacion:
                e = {"error_promedio": None, "error_maximo": None, "n": 0}
            fila.update(e)
            for paso in r.iteraciones:
                paso["observado"] = observados_por_t.get(round(paso["t"], 9))
                paso["P"] = modelo.P(paso["t"])
                paso["T_ent"] = modelo.T_entrada(paso["t"])
        rk4 = resultados[3]
        if rk4.iteraciones:
            for fila, r in zip(comparacion, resultados):
                if r.iteraciones and r is not rk4:
                    fila["dif_rk4"] = errores_serie(rk4.datos_grafica["y"],
                                                    r.datos_grafica["y"])["error_maximo"]
                else:
                    fila["dif_rk4"] = None if r is not rk4 else 0.0

        series = [serie("Historial", [{"x": t, "y": (None if math.isnan(v) else float(v))}
                                      for t, v in zip(datos["t"], temps)], "#0d3b66", radio=3,
                        linea=True, grosor=3)]
        for r, color in zip(resultados, COLORES):
            if r.iteraciones:
                series.append(serie(r.metodo, [{"x": t, "y": y} for t, y in
                                               zip(r.datos_grafica["t"], r.datos_grafica["y"])],
                                    color, linea=True, radio=0, discontinua=r.metodo == "Euler"))
        ctx.update({
            "datos": datos, "resultados": resultados, "comparacion": comparacion, "alfa": alfa,
            "alfa_sug": alfa_sug, "beta": beta, "P_idle": P_idle, "h": h, "T0": T0, "t0": t0,
            "horas": horas, "pasos": pasos, "fecha_sel": fecha,
            "graf": grafica("scatter", f"Temperatura simulada vs. historial ({fecha:%Y-%m-%d}, "
                                       f"{horas} h, h = {h:g} h)",
                            "t (horas desde 00:00)", "Temperatura (°C)", series),
        })
    except ErrorValidacion as exc:
        form.errores.append(str(exc))
    return render_template("edo.html", **ctx)
