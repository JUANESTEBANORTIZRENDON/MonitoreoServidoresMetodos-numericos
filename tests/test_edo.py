"""EDO: Euler, Heun, Ralston y RK4 sobre ecuaciones con solución conocida."""
import math

import pytest

from app.metodos_numericos import ErrorValidacion, Euler, Heun, ModeloTermicoEDO, Ralston, RungeKutta4

# dy/dt = y - t² + 1, y(0) = 0.5  →  y(t) = (t + 1)² - 0.5 e^t
f = lambda t, y: y - t ** 2 + 1
exacta = lambda t: (t + 1) ** 2 - 0.5 * math.exp(t)


def error_final(clase, h):
    n = int(round(2.0 / h))
    return abs(clase(f, 0.0, 0.5, h, n).resolver().resultado - exacta(2.0))


def test_resultados_contra_solucion_exacta():
    assert error_final(Euler, 0.2) < 0.6
    assert error_final(Heun, 0.2) < 0.1
    assert error_final(Ralston, 0.2) < 0.1
    assert error_final(Heun, 0.2) < error_final(Euler, 0.2) / 5
    assert error_final(RungeKutta4, 0.2) < 2e-4   # 1.09e-4 según Burden & Faires


def test_valores_de_referencia_de_libro():
    # Valores clásicos (Burden & Faires) con h = 0.2 en t = 2
    assert Euler(f, 0, 0.5, 0.2, 10).resolver().resultado == pytest.approx(4.8657845, abs=1e-6)
    assert RungeKutta4(f, 0, 0.5, 0.2, 10).resolver().resultado == pytest.approx(5.3053630, abs=1e-6)


def test_orden_de_convergencia():
    for clase, orden in ((Euler, 1), (Heun, 2), (Ralston, 2), (RungeKutta4, 4)):
        e1, e2 = error_final(clase, 0.1), error_final(clase, 0.05)
        assert math.log2(e1 / e2) == pytest.approx(orden, abs=0.3)


def test_heun_y_ralston_difieren_en_edo_no_lineal():
    g = lambda t, y: -y ** 2 + t
    a = Heun(g, 0, 1, 0.25, 8).resolver().resultado
    b = Ralston(g, 0, 1, 0.25, 8).resolver().resultado
    assert a != b and abs(a - b) < 0.05


def test_decaimiento_exponencial_y_pendientes():
    r = RungeKutta4(lambda t, y: -0.35 * y, 0, 10, 1.0, 5).resolver()
    z = -0.35  # λh
    factor_rk4 = 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24   # amplificación teórica de RK4
    assert r.resultado == pytest.approx(10 * factor_rk4 ** 5, rel=1e-12)
    assert r.resultado == pytest.approx(10 * math.exp(-1.75), rel=1e-3)  # cercano a la exacta
    assert set(r.iteraciones[0]["ks"]) == {"k1", "k2", "k3", "k4"}
    assert len(r.iteraciones) == 6


def test_modelo_termico_con_datos_del_excel(repo):
    from datetime import datetime
    lecturas = repo.rango(datetime(2026, 8, 1), 24)
    t = repo.horas_relativas(lecturas)
    modelo = ModeloTermicoEDO(0.045, 0.35, 150, t, [l.potencia for l in lecturas],
                              [l.temp_entrada for l in lecturas])
    T0 = lecturas[0].temp_servidor
    sol = [c(modelo.f, 0, T0, 1.0, 24).resolver() for c in (Euler, Heun, Ralston, RungeKutta4)]
    assert all(len(s.iteraciones) == 25 for s in sol)
    # métodos de orden 2 más cerca de RK4 que Euler
    assert abs(sol[1].resultado - sol[3].resultado) < abs(sol[0].resultado - sol[3].resultado)
    # Interpolación lineal de entradas entre horas
    assert modelo.P(0.5) == pytest.approx((lecturas[0].potencia + lecturas[1].potencia) / 2)


def test_valida_paso():
    with pytest.raises(ErrorValidacion):
        Euler(f, 0, 1, 0, 10).resolver()
    with pytest.raises(ErrorValidacion):
        Euler(f, 0, 1, 0.1, 0).resolver()


def test_interpolacion_lineal_de_entradas():
    from app.metodos_numericos import interpolacion_lineal
    assert interpolacion_lineal([0, 1, 2], [10, 20, 40], 1.5) == pytest.approx(30)
    with pytest.raises(ErrorValidacion):
        interpolacion_lineal([0, 1], [0, 1], 3)


def test_errores_serie_ignora_ausentes():
    from app.metodos_numericos import errores_serie
    e = errores_serie([50.0, float("nan"), 52.0], [49.0, 70.0, 54.0])
    assert e["n"] == 2
    assert e["error_promedio"] == pytest.approx(1.5)
    assert e["error_maximo"] == pytest.approx(2.0)
