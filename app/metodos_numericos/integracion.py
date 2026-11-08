"""Integración numérica sobre datos tabulados equiespaciados.

Trapecio compuesto, Simpson 1/3 compuesto, Simpson 3/8 compuesto y Romberg.
"""
from __future__ import annotations

from typing import Sequence

from .base import ErrorValidacion, MetodoNumerico, ResultadoMetodo, validar_finito


def paso_uniforme(xs: Sequence[float]) -> float:
    """Devuelve h y verifica que los nodos estén equiespaciados."""
    if len(xs) < 2:
        raise ErrorValidacion("Se necesitan al menos 2 puntos (1 subintervalo).")
    h = xs[1] - xs[0]
    if h <= 0:
        raise ErrorValidacion("Los nodos deben estar ordenados de forma creciente.")
    for i in range(1, len(xs) - 1):
        if abs((xs[i + 1] - xs[i]) - h) > 1e-9 * max(1.0, abs(h)):
            raise ErrorValidacion("Los nodos deben estar equiespaciados (paso h constante).")
    return h


class _ReglaCompuesta(MetodoNumerico):
    """Integral ≈ factor·h·Σ w_i f(x_i)."""

    divisor = 1  # el número de subintervalos debe ser múltiplo de este valor

    def __init__(self, xs: Sequence[float], ys: Sequence[float]):
        self.xs = list(xs)
        self.ys = list(ys)

    def _validar(self) -> None:
        if len(self.xs) != len(self.ys):
            raise ErrorValidacion("Debe haber un valor de potencia por cada instante.")
        self.ys = [validar_finito(v, "f(x_i)") for v in self.ys]
        self.h = paso_uniforme(self.xs)
        self.n = len(self.xs) - 1
        self._validar_n()

    def _validar_n(self) -> None:
        return None

    def pesos(self) -> list[int]:
        raise NotImplementedError

    factor_txt = ""

    def factor(self) -> float:
        raise NotImplementedError

    def _calcular(self) -> ResultadoMetodo:
        pesos = self.pesos()
        filas = []
        suma = 0.0
        for i, (x, y, w) in enumerate(zip(self.xs, self.ys, pesos)):
            suma += w * y
            filas.append({"i": i, "x_i": x, "f_x": y, "peso": w, "producto": w * y})
        sumas = self._sumas_intermedias()
        valor = self.factor() * suma
        return ResultadoMetodo(
            metodo=self.nombre, resultado=valor, iteraciones=filas, convergencia=True,
            mensaje=f"{self.nombre}: n = {self.n}, h = {self.h:.5f}, integral = {valor:.5f}",
            extra={"n": self.n, "h": self.h, "suma_ponderada": suma, "factor": self.factor(),
                   "factor_txt": self.factor_txt, "sumas": sumas},
        )

    def _sumas_intermedias(self) -> dict:
        return {}


class TrapecioCompuesto(_ReglaCompuesta):
    """I ≈ (h/2)[f0 + 2Σ f_i + f_n]"""

    nombre = "Trapecio compuesto"
    factor_txt = "h/2"

    def pesos(self) -> list[int]:
        return [1] + [2] * (self.n - 1) + [1] if self.n >= 1 else [1]

    def factor(self) -> float:
        return self.h / 2.0

    def _sumas_intermedias(self) -> dict:
        return {"extremos": self.ys[0] + self.ys[-1], "interiores": sum(self.ys[1:-1])}


class Simpson13Compuesto(_ReglaCompuesta):
    """I ≈ (h/3)[f0 + 4Σ f_impar + 2Σ f_par + f_n]; n par."""

    nombre = "Simpson 1/3 compuesto"
    factor_txt = "h/3"
    divisor = 2

    def _validar_n(self) -> None:
        if self.n < 2 or self.n % 2 != 0:
            raise ErrorValidacion(
                f"Simpson 1/3 requiere un número par de subintervalos; se tienen n = {self.n}.")

    def pesos(self) -> list[int]:
        return [1 if i in (0, self.n) else (4 if i % 2 == 1 else 2) for i in range(self.n + 1)]

    def factor(self) -> float:
        return self.h / 3.0

    def _sumas_intermedias(self) -> dict:
        return {"extremos": self.ys[0] + self.ys[-1],
                "impares": sum(self.ys[i] for i in range(1, self.n, 2)),
                "pares": sum(self.ys[i] for i in range(2, self.n, 2))}


class Simpson38Compuesto(_ReglaCompuesta):
    """I ≈ (3h/8)[f0 + 3Σ f_(i no múltiplo de 3) + 2Σ f_(múltiplo de 3) + f_n]; n múltiplo de 3."""

    nombre = "Simpson 3/8 compuesto"
    factor_txt = "3h/8"
    divisor = 3

    def _validar_n(self) -> None:
        if self.n < 3 or self.n % 3 != 0:
            raise ErrorValidacion(
                f"Simpson 3/8 requiere un número de subintervalos múltiplo de 3; se tienen n = {self.n}.")

    def pesos(self) -> list[int]:
        return [1 if i in (0, self.n) else (2 if i % 3 == 0 else 3) for i in range(self.n + 1)]

    def factor(self) -> float:
        return 3.0 * self.h / 8.0

    def _sumas_intermedias(self) -> dict:
        return {"extremos": self.ys[0] + self.ys[-1],
                "no_multiplos_3": sum(self.ys[i] for i in range(1, self.n) if i % 3 != 0),
                "multiplos_3": sum(self.ys[i] for i in range(3, self.n, 3))}


def niveles_romberg(n: int) -> list[int]:
    """Cadena de refinamientos n0, 2n0, 4n0, ..., n compatibles con los datos.

    Cada trapecio de Romberg usa un subconjunto de los nodos disponibles, por lo que
    los números de subintervalos deben dividir a n y duplicarse en cada nivel.
    """
    if n < 2:
        raise ErrorValidacion("Romberg necesita al menos 2 subintervalos.")
    m = 0
    while n % (2 ** (m + 1)) == 0:
        m += 1
    if m == 0:
        raise ErrorValidacion(
            f"Romberg requiere que n sea par para poder refinar (n = {n}); "
            "no es posible construir trapecios con paso h y 2h a partir de los datos.")
    n0 = n // (2 ** m)
    return [n0 * 2 ** k for k in range(m + 1)]


class Romberg(MetodoNumerico):
    """R(k,0): trapecio con n_k subintervalos;
    R(k,j) = R(k,j-1) + [R(k,j-1) - R(k-1,j-1)] / (4^j - 1)."""

    nombre = "Romberg"

    def __init__(self, xs: Sequence[float], ys: Sequence[float]):
        self.xs = list(xs)
        self.ys = list(ys)

    def _validar(self) -> None:
        if len(self.xs) != len(self.ys):
            raise ErrorValidacion("Debe haber un valor de f por cada nodo.")
        self.ys = [validar_finito(v, "f(x_i)") for v in self.ys]
        self.h = paso_uniforme(self.xs)
        self.n = len(self.xs) - 1
        self.niveles = niveles_romberg(self.n)

    def _calcular(self) -> ResultadoMetodo:
        R: list[list[float | None]] = []
        detalle = []
        m = len(self.niveles)
        for k, nk in enumerate(self.niveles):
            salto = self.n // nk
            xs_k = self.xs[::salto]
            ys_k = self.ys[::salto]
            trap = TrapecioCompuesto(xs_k, ys_k).resolver()
            fila: list[float | None] = [None] * m
            fila[0] = trap.resultado
            for j in range(1, k + 1):
                fila[j] = fila[j - 1] + (fila[j - 1] - R[k - 1][j - 1]) / (4 ** j - 1)
            R.append(fila)
            detalle.append({"nivel": k, "subintervalos": nk, "h": trap.extra["h"],
                            "trapecio": trap.resultado, "fila": fila})
        valor = R[-1][m - 1]
        error = abs(R[-1][m - 1] - R[-1][m - 2]) if m >= 2 else None
        return ResultadoMetodo(
            metodo=self.nombre, resultado=valor, iteraciones=detalle, error=error,
            convergencia=True,
            mensaje=(f"Tabla de Romberg de {m} niveles (n = {', '.join(map(str, self.niveles))}); "
                     f"mejor estimación R({m - 1},{m - 1}) = {valor:.5f}"),
            extra={"tabla": R, "niveles": self.niveles},
        )
