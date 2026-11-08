"""Errores entre una serie simulada y una observada (usado por el módulo de EDO)."""
from __future__ import annotations

from typing import Sequence

import numpy as np

from .base import ErrorValidacion


def errores_serie(observados: Sequence[float], simulados: Sequence[float]) -> dict:
    """Error absoluto punto a punto, ignorando posiciones sin dato (NaN).

    Devuelve el error promedio, el máximo y la raíz del error cuadrático medio (RMSE).
    """
    obs = np.asarray(observados, dtype=float)
    sim = np.asarray(simulados, dtype=float)
    if obs.shape != sim.shape:
        raise ErrorValidacion("Las series a comparar deben tener la misma longitud.")
    mascara = ~np.isnan(obs) & ~np.isnan(sim)
    if not mascara.any():
        raise ErrorValidacion("No hay pares de datos válidos para comparar.")
    abs_err = np.abs(obs[mascara] - sim[mascara])
    return {
        "n": int(mascara.sum()),
        "error_promedio": float(abs_err.sum() / abs_err.size),
        "error_maximo": float(abs_err.max()),
        "rmse": float(np.sqrt((abs_err ** 2).sum() / abs_err.size)),
    }
