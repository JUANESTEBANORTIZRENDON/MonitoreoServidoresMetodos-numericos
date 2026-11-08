"""Paquete con todas las fórmulas y algoritmos numéricos implementados manualmente.

Ningún controlador ni servicio debe contener fórmulas: todos importan desde aquí.
"""
from .base import ErrorValidacion, MetodoNumerico, ResultadoMetodo, tabla_comparativa
from .edo import Euler, Heun, ModeloTermicoEDO, Ralston, RungeKutta4, alfa_estado_estacionario
from .errores import errores_serie
from .integracion import Romberg, Simpson13Compuesto, Simpson38Compuesto, TrapecioCompuesto
from .interpolacion import interpolacion_lineal

__all__ = [
    "ErrorValidacion", "MetodoNumerico", "ResultadoMetodo", "tabla_comparativa",
    "Euler", "Heun", "Ralston", "RungeKutta4", "ModeloTermicoEDO", "alfa_estado_estacionario",
    "errores_serie",
    "TrapecioCompuesto", "Simpson13Compuesto", "Simpson38Compuesto", "Romberg",
    "interpolacion_lineal",
]
