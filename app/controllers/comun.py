"""Utilidades compartidas por los controladores: lectura y validación de formularios.

Aquí no hay fórmulas numéricas; solo conversión segura de entradas y manejo de errores.
"""
from __future__ import annotations

import logging
import math
from datetime import date, datetime
from typing import Callable

from flask import request

from app.metodos_numericos import ErrorValidacion, ResultadoMetodo
from app.metodos_numericos.base import resultado_fallido

logger = logging.getLogger(__name__)


class Formulario:
    """Lee parámetros GET validando tipo y rango; acumula mensajes de error."""

    def __init__(self, fuente=None):
        self.fuente = fuente if fuente is not None else request.args
        self.errores: list[str] = []
        self.valores: dict = {}

    def float(self, nombre: str, defecto: float, etiqueta: str, minimo: float | None = None,
              maximo: float | None = None) -> float:
        crudo = (self.fuente.get(nombre) or "").strip().replace(",", ".")
        valor = defecto
        if crudo:
            try:
                valor = float(crudo)
                if not math.isfinite(valor):
                    raise ValueError
            except ValueError:
                self.errores.append(f"«{etiqueta}» debe ser un número (se recibió «{crudo[:20]}»).")
                valor = defecto
        if minimo is not None and valor < minimo:
            self.errores.append(f"«{etiqueta}» debe ser ≥ {minimo}.")
            valor = defecto
        if maximo is not None and valor > maximo:
            self.errores.append(f"«{etiqueta}» debe ser ≤ {maximo}.")
            valor = defecto
        self.valores[nombre] = valor
        return valor

    def int(self, nombre: str, defecto: int, etiqueta: str, minimo: int | None = None,
            maximo: int | None = None) -> int:
        crudo = (self.fuente.get(nombre) or "").strip()
        valor = defecto
        if crudo:
            try:
                valor = int(crudo)
            except ValueError:
                self.errores.append(f"«{etiqueta}» debe ser un número entero.")
                valor = defecto
        if minimo is not None and valor < minimo:
            self.errores.append(f"«{etiqueta}» debe ser ≥ {minimo}.")
            valor = defecto
        if maximo is not None and valor > maximo:
            self.errores.append(f"«{etiqueta}» debe ser ≤ {maximo}.")
            valor = defecto
        self.valores[nombre] = valor
        return valor

    def fecha(self, nombre: str, defecto: date | None, etiqueta: str, minimo: date | None = None,
              maximo: date | None = None) -> date | None:
        crudo = (self.fuente.get(nombre) or "").strip()
        valor = defecto
        if crudo:
            try:
                valor = datetime.strptime(crudo, "%Y-%m-%d").date()
            except ValueError:
                self.errores.append(f"«{etiqueta}» debe tener formato AAAA-MM-DD.")
                valor = defecto
        if valor is not None and minimo and valor < minimo:
            self.errores.append(f"«{etiqueta}» no puede ser anterior a {minimo:%Y-%m-%d}.")
            valor = defecto
        if valor is not None and maximo and valor > maximo:
            self.errores.append(f"«{etiqueta}» no puede ser posterior a {maximo:%Y-%m-%d}.")
            valor = defecto
        self.valores[nombre] = valor
        return valor

    def opcion(self, nombre: str, opciones, defecto):
        crudo = (self.fuente.get(nombre) or "").strip()
        valor = crudo if crudo in opciones else defecto
        if crudo and crudo not in opciones:
            self.errores.append(f"Opción no válida para «{nombre}».")
        self.valores[nombre] = valor
        return valor

    def texto(self, nombre: str, maximo: int = 60) -> str:
        valor = (self.fuente.get(nombre) or "").strip()[:maximo]
        self.valores[nombre] = valor
        return valor

    def bandera(self, nombre: str) -> bool:
        valor = self.fuente.get(nombre) in ("1", "on", "true")
        self.valores[nombre] = valor
        return valor


def ejecutar_seguro(nombre: str, fabrica: Callable[[], ResultadoMetodo]) -> ResultadoMetodo:
    """Ejecuta ``fabrica`` (que llama a resolver()) y convierte errores en mensajes claros."""
    try:
        return fabrica()
    except ErrorValidacion as exc:
        return resultado_fallido(nombre, str(exc))
    except (ArithmeticError, ValueError) as exc:
        logger.exception("Fallo numérico en %s", nombre)
        return resultado_fallido(nombre, "El método no pudo completarse por un problema numérico "
                                         f"({type(exc).__name__}). Revise los parámetros.")


def serie(nombre: str, datos, color: str | None = None, **opciones) -> dict:
    d = {"nombre": nombre, "datos": datos}
    if color:
        d["color"] = color
    d.update(opciones)
    return d


def grafica(tipo: str, titulo: str, x_titulo: str, y_titulo: str, series: list[dict],
            labels: list | None = None, **opciones) -> dict:
    """Descripción neutra de una gráfica; static/js/charts.js la convierte a Chart.js."""
    g = {"tipo": tipo, "titulo": titulo, "x_titulo": x_titulo, "y_titulo": y_titulo,
         "series": series}
    if labels is not None:
        g["labels"] = labels
    g.update(opciones)
    return g
