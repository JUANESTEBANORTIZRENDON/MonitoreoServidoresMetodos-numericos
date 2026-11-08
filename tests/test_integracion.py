"""Integración: exactitud, condiciones de Simpson y estructura de Romberg."""
import math

import pytest

from app.metodos_numericos import (ErrorValidacion, Romberg, Simpson13Compuesto, Simpson38Compuesto,
                                   TrapecioCompuesto)
from app.metodos_numericos.integracion import niveles_romberg


def nodos(n, a=0.0, b=24.0, f=lambda t: 250 + 40 * math.sin(math.pi * t / 24)):
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    return xs, [f(x) for x in xs]


EXACTA = 250 * 24 + 40 * 48 / math.pi


def test_trapecio_exacto_para_recta():
    xs, ys = nodos(24, f=lambda t: 200 + 3 * t)
    assert TrapecioCompuesto(xs, ys).resolver().resultado == pytest.approx(200 * 24 + 1.5 * 24 ** 2)


def test_simpson_exacto_para_cubica():
    f = lambda t: t ** 3 - 2 * t + 5
    exacta = 24 ** 4 / 4 - 24 ** 2 + 5 * 24
    xs, ys = nodos(24, f=f)
    assert Simpson13Compuesto(xs, ys).resolver().resultado == pytest.approx(exacta)
    assert Simpson38Compuesto(xs, ys).resolver().resultado == pytest.approx(exacta)


def test_simpson_13_requiere_n_par():
    xs, ys = nodos(9)
    with pytest.raises(ErrorValidacion, match="par"):
        Simpson13Compuesto(xs, ys).resolver()


def test_simpson_38_requiere_multiplo_de_3():
    xs, ys = nodos(10)
    with pytest.raises(ErrorValidacion, match="múltiplo de 3"):
        Simpson38Compuesto(xs, ys).resolver()
    xs, ys = nodos(9)
    assert Simpson38Compuesto(xs, ys).resolver().convergencia


def test_pesos_simpson():
    xs, ys = nodos(6)
    r13 = Simpson13Compuesto(xs, ys).resolver()
    r38 = Simpson38Compuesto(xs, ys).resolver()
    assert [f["peso"] for f in r13.iteraciones] == [1, 4, 2, 4, 2, 4, 1]
    assert [f["peso"] for f in r38.iteraciones] == [1, 3, 3, 2, 3, 3, 1]


def test_estructura_tabla_romberg():
    xs, ys = nodos(24)
    r = Romberg(xs, ys).resolver()
    tabla = r.extra["tabla"]
    assert r.extra["niveles"] == [3, 6, 12, 24]
    assert len(tabla) == 4
    for k, fila in enumerate(tabla):
        assert all(v is not None for v in fila[:k + 1])      # triangular inferior
        assert all(v is None for v in fila[k + 1:])
    assert tabla[0][0] == pytest.approx(TrapecioCompuesto(xs[::8], ys[::8]).resolver().resultado)
    assert tabla[3][0] == pytest.approx(TrapecioCompuesto(xs, ys).resolver().resultado)
    # Richardson mejora la estimación del trapecio
    assert abs(r.resultado - EXACTA) < abs(tabla[3][0] - EXACTA)
    assert r.resultado == pytest.approx(EXACTA, abs=1e-6)


def test_niveles_romberg_compatibles():
    assert niveles_romberg(8) == [1, 2, 4, 8]
    assert niveles_romberg(48) == [3, 6, 12, 24, 48]
    with pytest.raises(ErrorValidacion):
        niveles_romberg(9)


def test_rechaza_nodos_no_equiespaciados():
    with pytest.raises(ErrorValidacion, match="equiespaciados"):
        TrapecioCompuesto([0, 1, 3], [1, 1, 1]).resolver()


def test_energia_dia_del_excel(repo):
    from datetime import datetime
    lecturas = repo.rango(datetime(2026, 8, 1), 24)
    assert len(lecturas) == 25
    t = repo.horas_relativas(lecturas)
    P = [l.potencia for l in lecturas]
    valores = [c(t, P).resolver().resultado for c in (TrapecioCompuesto, Simpson13Compuesto,
                                                       Simpson38Compuesto, Romberg)]
    assert max(valores) - min(valores) < 0.01 * valores[0]   # métodos consistentes (<1 %)
    assert 4000 < valores[0] < 10000                          # Wh razonables en 24 h
