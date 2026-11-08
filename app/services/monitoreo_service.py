"""Servicio de monitoreo: prepara los datos del Excel que necesita cada módulo.

No contiene fórmulas de métodos numéricos; cuando requiere un cálculo numérico
(p. ej. la energía total del dashboard) llama a las clases de ``metodos_numericos``.
"""
from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta

import numpy as np
from flask import current_app

from app.metodos_numericos import ErrorValidacion, TrapecioCompuesto
from app.models.lectura_servidor import LecturaServidor
from app.models.repositorio_monitoreo import RepositorioMonitoreo


def obtener_repositorio() -> RepositorioMonitoreo:
    repo = current_app.extensions.get("repositorio_monitoreo")
    if repo is None:
        from app.services.excel_service import ErrorDatosExcel
        raise ErrorDatosExcel(current_app.extensions.get("error_datos", "Datos no disponibles."))
    return repo


def _media(v: np.ndarray) -> float | None:
    v = v[~np.isnan(v)]
    return float(v.sum() / v.size) if v.size else None


def _maximo(v: np.ndarray) -> float | None:
    v = v[~np.isnan(v)]
    return float(v.max()) if v.size else None


def _serie_json(v: np.ndarray) -> list:
    """Convierte NaN en None para que Chart.js muestre un hueco (no un cero)."""
    return [None if math.isnan(x) else float(x) for x in v]


def etiquetas(lecturas: list[LecturaServidor]) -> list[str]:
    return [l.fecha_hora.strftime("%Y-%m-%d %H:%M") for l in lecturas]


# --------------------------------------------------------------------- Dashboard
def resumen_dashboard(repo: RepositorioMonitoreo, desde: date | None, hasta: date | None,
                      estado: str | None) -> dict:
    lecturas = repo.filtrar(desde, hasta, estado or None)
    if not lecturas:
        raise ErrorValidacion("No hay registros que cumplan los filtros seleccionados.")
    temp = repo.vector(lecturas, "temp_servidor")
    cpu = repo.vector(lecturas, "cpu")
    ram = repo.vector(lecturas, "ram")
    conteo = {e: 0 for e in ("Normal", "Preventivo", "Crítico", "Sin dato")}
    for l in lecturas:
        conteo[l.estado] = conteo.get(l.estado, 0) + 1

    # Energía aproximada con trapecio compuesto: requiere registros consecutivos.
    energia_kwh, energia_nota = None, ""
    consecutivos = all((b.fecha_hora - a.fecha_hora) == timedelta(hours=1)
                       for a, b in zip(lecturas, lecturas[1:]))
    if len(lecturas) >= 2 and consecutivos:
        r = TrapecioCompuesto(repo.horas_relativas(lecturas), [l.potencia for l in lecturas]).resolver()
        energia_kwh = r.resultado / 1000.0
        energia_nota = (f"Trapecio compuesto sobre {len(lecturas) - 1} intervalos de 1 h "
                        f"({lecturas[0].fecha_hora:%Y-%m-%d %H:%M} a {lecturas[-1].fecha_hora:%Y-%m-%d %H:%M}).")
    else:
        energia_kwh = sum(l.potencia for l in lecturas) / 1000.0
        energia_nota = ("Registros no consecutivos (filtro por estado): se aproxima como "
                        "Σ P·(1 h), una suma de rectángulos.")

    return {
        "servidor": repo.servidor,
        "inicio": lecturas[0].fecha_hora, "fin": lecturas[-1].fecha_hora,
        "registros": len(lecturas),
        "temp_promedio": _media(temp), "temp_maxima": _maximo(temp),
        "cpu_promedio": _media(cpu), "ram_promedio": _media(ram),
        "energia_kwh": energia_kwh, "energia_nota": energia_nota,
        "conteo_estados": conteo, "ausentes": int(np.isnan(temp).sum()),
        "grafica": {"labels": etiquetas(lecturas), "temperatura": _serie_json(temp),
                    "cpu": _serie_json(cpu)},
        "resumen_mensual": repo.resumen,
        "resumen_global": repo.resumen_global,
    }


# --------------------------------------------------------------------- Historial
def historial_paginado(repo: RepositorioMonitoreo, desde, hasta, estado, texto, pagina: int,
                       por_pagina: int, orden: str, descendente: bool) -> dict:
    filtradas = repo.filtrar(desde, hasta, estado or None, texto)
    filtradas = repo.ordenar(filtradas, orden, descendente)
    total = len(filtradas)
    paginas = max(1, math.ceil(total / por_pagina))
    pagina = min(max(1, pagina), paginas)
    inicio = (pagina - 1) * por_pagina
    return {"filas": filtradas[inicio:inicio + por_pagina], "total": total, "pagina": pagina,
            "paginas": paginas, "por_pagina": por_pagina}


# --------------------------------------------------------------------- Periodos
def fechas_disponibles(repo: RepositorioMonitoreo, horas: int = 24) -> tuple[date, date]:
    """Primer y último día en que caben ``horas`` lecturas completas desde las 00:00."""
    ultimo = (repo.fin - timedelta(hours=horas)).date()
    if datetime.combine(ultimo, time()) + timedelta(hours=horas) > repo.fin:
        ultimo -= timedelta(days=1)
    return repo.inicio.date(), ultimo


def periodo(repo: RepositorioMonitoreo, fecha: date, horas: int) -> dict:
    """Lecturas de ``fecha 00:00`` a ``fecha 00:00 + horas`` (ambos extremos incluidos)."""
    if horas < 1:
        raise ErrorValidacion("El periodo debe tener al menos 1 hora.")
    inicio = datetime.combine(fecha, time())
    fin = inicio + timedelta(hours=horas)
    if inicio < repo.inicio or fin > repo.fin:
        raise ErrorValidacion(
            f"El periodo {inicio:%Y-%m-%d %H:%M} – {fin:%Y-%m-%d %H:%M} sale del rango del Excel "
            f"({repo.inicio:%Y-%m-%d %H:%M} – {repo.fin:%Y-%m-%d %H:%M}).")
    lecturas = repo.rango(inicio, horas)
    if len(lecturas) != horas + 1:
        raise ErrorValidacion("El periodo seleccionado no tiene lecturas horarias completas.")
    return {
        "lecturas": lecturas, "inicio": inicio, "fin": fin,
        "t": repo.horas_relativas(lecturas, inicio),
        "potencia": [l.potencia for l in lecturas],
        "temp_entrada": [l.temp_entrada for l in lecturas],
        "temp_servidor": repo.vector(lecturas, "temp_servidor"),
        "etiquetas": etiquetas(lecturas),
    }
