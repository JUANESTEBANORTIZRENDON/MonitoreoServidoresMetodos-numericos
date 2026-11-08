"""Ecuaciones diferenciales ordinarias: Euler, Heun, Ralston y Runge-Kutta 4.

Todos resuelven dy/dt = f(t, y) con y(t0) = y0, paso h y n pasos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .base import (ErrorValidacion, MetodoNumerico, ResultadoMetodo, validar_finito,
                   validar_positivo)
from .interpolacion import interpolacion_lineal

FuncionEDO = Callable[[float, float], float]
MAX_PASOS = 5000


class _MetodoEDO(MetodoNumerico):
    orden = 1

    def __init__(self, f: FuncionEDO, t0: float, y0: float, h: float, n_pasos: int):
        self.f = f
        self.t0 = t0
        self.y0 = y0
        self.h = h
        self.n_pasos = n_pasos

    def _validar(self) -> None:
        self.t0 = validar_finito(self.t0, "t0")
        self.y0 = validar_finito(self.y0, "condición inicial y0")
        self.h = validar_positivo(self.h, "paso h")
        try:
            self.n_pasos = int(self.n_pasos)
        except (TypeError, ValueError):
            raise ErrorValidacion("El número de pasos debe ser entero.")
        if self.n_pasos < 1 or self.n_pasos > MAX_PASOS:
            raise ErrorValidacion(f"El número de pasos debe estar entre 1 y {MAX_PASOS}.")

    def _paso(self, t: float, y: float) -> tuple[float, dict]:
        raise NotImplementedError

    def _calcular(self) -> ResultadoMetodo:
        t, y = self.t0, self.y0
        filas = [{"paso": 0, "t": t, "y": y, "ks": {}, "y_siguiente": None}]
        ts, ys = [t], [y]
        for i in range(1, self.n_pasos + 1):
            y_nuevo, ks = self._paso(t, y)
            if not (abs(y_nuevo) < 1e12):
                raise ErrorValidacion(
                    f"{self.nombre}: la solución se volvió inestable en el paso {i}; reduzca h.")
            filas[-1]["ks"] = ks
            filas[-1]["y_siguiente"] = y_nuevo
            t = self.t0 + i * self.h
            y = y_nuevo
            filas.append({"paso": i, "t": t, "y": y, "ks": {}, "y_siguiente": None})
            ts.append(t)
            ys.append(y)
        return ResultadoMetodo(
            metodo=self.nombre, resultado=y, iteraciones=filas, convergencia=True,
            mensaje=f"{self.nombre} (orden {self.orden}): y({t:.5f}) ≈ {y:.5f} tras {self.n_pasos} pasos.",
            datos_grafica={"t": ts, "y": ys}, extra={"orden": self.orden, "h": self.h},
        )


class Euler(_MetodoEDO):
    """y_{i+1} = y_i + h·k1,  k1 = f(t_i, y_i)."""

    nombre = "Euler"
    orden = 1

    def _paso(self, t, y):
        k1 = self.f(t, y)
        return y + self.h * k1, {"k1": k1}


class Heun(_MetodoEDO):
    """k1 = f(t, y); k2 = f(t + h, y + h k1); y_{i+1} = y_i + h(k1 + k2)/2."""

    nombre = "Heun (Euler mejorado)"
    orden = 2

    def _paso(self, t, y):
        h = self.h
        k1 = self.f(t, y)
        k2 = self.f(t + h, y + h * k1)
        return y + h * (k1 + k2) / 2.0, {"k1": k1, "k2": k2}


class Ralston(_MetodoEDO):
    """k1 = f(t, y); k2 = f(t + 3h/4, y + 3h k1/4); y_{i+1} = y_i + h(k1 + 2k2)/3."""

    nombre = "Ralston (2.º orden)"
    orden = 2

    def _paso(self, t, y):
        h = self.h
        k1 = self.f(t, y)
        k2 = self.f(t + 0.75 * h, y + 0.75 * h * k1)
        return y + h * (k1 + 2.0 * k2) / 3.0, {"k1": k1, "k2": k2}


class RungeKutta4(_MetodoEDO):
    """y_{i+1} = y_i + h(k1 + 2k2 + 2k3 + k4)/6."""

    nombre = "Runge-Kutta 4"
    orden = 4

    def _paso(self, t, y):
        h = self.h
        k1 = self.f(t, y)
        k2 = self.f(t + h / 2.0, y + h * k1 / 2.0)
        k3 = self.f(t + h / 2.0, y + h * k2 / 2.0)
        k4 = self.f(t + h, y + h * k3)
        return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0, {"k1": k1, "k2": k2, "k3": k3, "k4": k4}


def alfa_estado_estacionario(beta: float, P_idle: float, potencias: Sequence[float],
                             temperaturas: Sequence[float], temperaturas_entrada: Sequence[float]) -> float | None:
    """α que hace coincidir el equilibrio medio del modelo con los datos.

    En equilibrio dT/dt = 0  ⇒  α(P̄ - P_idle) = β(T - T_ent)‾  ⇒  α = β(T - T_ent)‾ / (P̄ - P_idle).
    Solo se usan los registros con temperatura válida. Es una sugerencia de calibración.
    """
    pares = [(p, t, ti) for p, t, ti in zip(potencias, temperaturas, temperaturas_entrada)
             if t is not None and t == t]
    if not pares:
        return None
    dp = sum(p - P_idle for p, _, _ in pares) / len(pares)
    dt = sum(t - ti for _, t, ti in pares) / len(pares)
    if abs(dp) < 1e-12:
        return None
    return beta * dt / dp


@dataclass
class ModeloTermicoEDO:
    """dT/dt = α(P(t) - P_idle) - β(T - T_entrada(t)).

    P(t) y T_entrada(t) provienen del Excel (lecturas horarias). Cuando un método
    evalúa instantes intermedios (t + h/2, t + 3h/4) se interpolan linealmente.
    """

    alfa: float
    beta: float
    P_idle: float
    tiempos: Sequence[float]
    potencias: Sequence[float]
    temperaturas_entrada: Sequence[float]

    def validar(self) -> None:
        validar_finito(self.alfa, "α")
        validar_positivo(self.beta, "β")
        validar_finito(self.P_idle, "P_idle")
        if len(self.tiempos) < 2:
            raise ErrorValidacion("El periodo debe contener al menos dos lecturas.")

    def P(self, t: float) -> float:
        return interpolacion_lineal(self.tiempos, self.potencias, t)

    def T_entrada(self, t: float) -> float:
        return interpolacion_lineal(self.tiempos, self.temperaturas_entrada, t)

    def f(self, t: float, T: float) -> float:
        return self.alfa * (self.P(t) - self.P_idle) - self.beta * (T - self.T_entrada(t))
