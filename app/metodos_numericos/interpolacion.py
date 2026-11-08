"""Interpolación lineal por tramos.

La usa el módulo de EDO para obtener P(t) y T_entrada(t) en instantes entre
lecturas horarias (t + h/2 en RK4, t + 3h/4 en Ralston, o pasos h ≠ 1).
"""
from __future__ import annotations

from bisect import bisect_right
from typing import Sequence

from .base import ErrorValidacion


def interpolacion_lineal(xs: Sequence[float], ys: Sequence[float], x: float) -> float:
    """y(x) = y0 + (y1 - y0)(x - x0)/(x1 - x0) entre los dos puntos vecinos (sin extrapolar)."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise ErrorValidacion("La interpolación lineal requiere al menos dos puntos.")
    if x < xs[0] - 1e-12 or x > xs[-1] + 1e-12:
        raise ErrorValidacion(f"t = {x:.5f} está fuera del rango de datos [{xs[0]}, {xs[-1]}].")
    i = min(max(bisect_right(xs, x) - 1, 0), len(xs) - 2)
    x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
