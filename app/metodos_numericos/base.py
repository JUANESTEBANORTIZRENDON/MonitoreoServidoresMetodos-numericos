"""Componentes comunes a todos los métodos numéricos.

Contiene:
- ``ResultadoMetodo``: estructura uniforme de salida.
- ``MetodoNumerico``: clase base abstracta con el método público ``resolver()``.
- ``ErrorValidacion``: excepción con mensajes comprensibles para estudiantes.
- Funciones puras auxiliares de validación y preparación de tablas.
"""
from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable


class ErrorValidacion(ValueError):
    """Error de datos de entrada explicado en lenguaje claro."""


@dataclass
class ResultadoMetodo:
    """Resultado uniforme que entrega cualquier método numérico.

    Atributos
    ---------
    metodo: nombre legible del método.
    resultado: valor final (precisión completa; se redondea solo al mostrar).
    iteraciones: lista de diccionarios, una fila por paso o nodo.
    error: último error estimado, si el método lo calcula.
    convergencia: True si el método se aplicó correctamente.
    mensaje: explicación breve del resultado.
    datos_grafica: series listas para Chart.js.
    extra: información adicional propia del método (tablas, pesos, sumas...).
    tiempo_ms: tiempo de ejecución medido por ``resolver()``.
    """

    metodo: str
    resultado: Any = None
    iteraciones: list[dict] = field(default_factory=list)
    error: float | None = None
    convergencia: bool = False
    mensaje: str = ""
    datos_grafica: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)
    tiempo_ms: float = 0.0

    @property
    def numero_iteraciones(self) -> int:
        return len(self.iteraciones)


class MetodoNumerico(ABC):
    """Interfaz común. Las subclases implementan ``_validar`` y ``_calcular``.

    ``resolver()`` es el único método público: valida, mide el tiempo y
    devuelve un ``ResultadoMetodo``.
    """

    nombre: str = "Método numérico"

    def resolver(self) -> ResultadoMetodo:
        self._validar()
        inicio = time.perf_counter()
        resultado = self._calcular()
        resultado.tiempo_ms = (time.perf_counter() - inicio) * 1000.0
        return resultado

    def _validar(self) -> None:  # pragma: no cover - por defecto no valida nada
        return None

    @abstractmethod
    def _calcular(self) -> ResultadoMetodo:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Funciones puras auxiliares
# ---------------------------------------------------------------------------

def validar_finito(valor: Any, nombre: str) -> float:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        v = math.nan
    if valor is None or not math.isfinite(v):
        raise ErrorValidacion(f"El valor de «{nombre}» debe ser un número real válido.")
    return v


def validar_positivo(valor: Any, nombre: str) -> float:
    v = validar_finito(valor, nombre)
    if v <= 0:
        raise ErrorValidacion(f"«{nombre}» debe ser mayor que cero (se recibió {v}).")
    return v


def tabla_comparativa(resultados: Iterable[ResultadoMetodo]) -> list[dict]:
    """Prepara una tabla resumen de varios métodos aplicados al mismo problema."""
    return [
        {
            "metodo": r.metodo,
            "resultado": r.resultado if not isinstance(r.resultado, (list, dict)) else None,
            "iteraciones": r.numero_iteraciones,
            "error": r.error,
            "convergencia": r.convergencia,
            "tiempo_ms": r.tiempo_ms,
            "mensaje": r.mensaje,
        }
        for r in resultados
    ]


def resultado_fallido(metodo: str, mensaje: str) -> ResultadoMetodo:
    """Resultado para métodos que no pueden aplicarse (p. ej. condición no cumplida)."""
    return ResultadoMetodo(metodo=metodo, convergencia=False, mensaje=mensaje)
