# Métodos numéricos

Todos están en `app/metodos_numericos/`. Cada clase hereda de `MetodoNumerico` y se usa así:

```python
resultado = TrapecioCompuesto(t, P).resolver()     # → ResultadoMetodo
resultado.resultado, resultado.iteraciones, resultado.error, resultado.convergencia, resultado.mensaje
```

Validaciones comunes (`base.py`): valores finitos (`validar_finito`) y positivos (`validar_positivo`).
Los errores se lanzan como `ErrorValidacion` con un mensaje comprensible para estudiantes.

| Archivo | Contenido |
|---|---|
| `base.py` | `ResultadoMetodo`, `MetodoNumerico`, `ErrorValidacion`, validaciones, `tabla_comparativa` |
| `integracion.py` | Trapecio, Simpson 1/3, Simpson 3/8, Romberg, `paso_uniforme`, `niveles_romberg` |
| `edo.py` | Euler, Heun, Ralston, RK4, `ModeloTermicoEDO`, `alfa_estado_estacionario` |
| `interpolacion.py` | `interpolacion_lineal` (entradas de la EDO entre horas) |
| `errores.py` | `errores_serie` (error promedio, máximo y RMSE ignorando datos ausentes) |

---

## 1. Integración numérica (`integracion.py`)

**Propósito**: calcular la energía consumida a partir de la potencia horaria.
E = ∫P(t) dt [Wh]; E_kWh = E/1000.

**Entradas**: `xs` (horas, equiespaciadas) y `ys` (potencia en W) tomadas del Excel.
**Validaciones**: misma longitud, valores finitos, nodos crecientes y equiespaciados (`paso_uniforme`).

| Clase | Fórmula | Condición |
|---|---|---|
| `TrapecioCompuesto` | (h/2)[P0 + 2ΣP_i + Pn] | n ≥ 1 |
| `Simpson13Compuesto` | (h/3)[P0 + 4Σimpar + 2Σpar + Pn] | **n par** |
| `Simpson38Compuesto` | (3h/8)[P0 + 3Σ(i no múltiplo de 3) + 2Σ(múltiplo de 3) + Pn] | **n múltiplo de 3** |
| `Romberg` | R_{k,0} = trapecio con n_k; R_{k,j} = R_{k,j−1} + (R_{k,j−1} − R_{k−1,j−1})/(4^j − 1) | n par |

**Salidas**: `iteraciones` con t_i, P_i, peso w_i y w_i·P_i; `extra` con h, n, factor, suma ponderada y
sumas intermedias (extremos, impares, pares…). Romberg entrega la tabla triangular y los niveles.

`niveles_romberg(n)` elige la cadena n0, 2n0, …, n que usa solo nodos existentes: para n = 24 →
3, 6, 12, 24 (4 niveles).

**Resultado 2026-08-01 (24 h)**: trapecio 6153.83000 Wh, Simpson 1/3 6160.22667 Wh,
Simpson 3/8 6158.42625 Wh, Romberg 6164.06916 Wh (6.16407 kWh).

**Aplicación**: costos de energía, dimensionamiento de UPS, cálculo de PUE. El Dashboard usa
`TrapecioCompuesto` para la energía total de los 3 meses (597.50927 kWh).

## 2. Ecuaciones diferenciales (`edo.py`)

**Propósito**: simular la temperatura del servidor (gemelo digital térmico).

dT/dt = f(t, T) = α(P(t) − P_idle) − β(T − T_entrada(t)) — `ModeloTermicoEDO`.

P(t) y T_entrada(t) se toman del Excel y se obtienen con `interpolacion_lineal` cuando el método
evalúa instantes intermedios (t + h/2, t + 3h/4) o cuando h ≠ 1:
y(x) = y0 + (y1 − y0)(x − x0)/(x1 − x0).

| Clase | Pendientes | Actualización | Orden |
|---|---|---|---|
| `Euler` | k1 = f(t, T) | T + h·k1 | 1 |
| `Heun` | k2 = f(t + h, T + h·k1) | T + h(k1 + k2)/2 | 2 |
| `Ralston` | k2 = f(t + 3h/4, T + 3h·k1/4) | T + h(k1 + 2k2)/3 | 2 |
| `RungeKutta4` | k2, k3 en t + h/2; k4 en t + h | T + h(k1 + 2k2 + 2k3 + k4)/6 | 4 |

**Entradas**: f, t0, T0, h, n_pasos (1–5000). Parámetros por defecto: α = 0.045 °C/(h·W),
β = 0.35 h⁻¹, P_idle = 150 W, h = 1 h, T0 = primera lectura válida del periodo.
**Validaciones**: h > 0, la duración debe ser múltiplo de h (controlador), detección de inestabilidad
(|T| > 1e12).
**Salidas**: tabla con t, T, P, T_ent, k1…k4, T_{i+1} y lectura histórica; serie para la gráfica.

`errores_serie(observados, simulados)` compara con el historial ignorando las horas sin temperatura
(error promedio, máximo y RMSE). `alfa_estado_estacionario` sugiere
α = β·(T − T_ent)‾ / (P − P_idle)‾.

**Resultado 2026-08-01 (α = 0.045)**: máx. |Euler − RK4| = 1.63407 °C, Heun/Ralston 0.21994 °C;
RK4 vs. historial: error promedio 19.43558 °C. Con α calibrado (0.11685) el error promedio baja a
3.83086 °C.

RK4 se usa como **referencia numérica de mayor orden, no como solución exacta**. Las pruebas verifican
el orden de convergencia (1, 2, 2, 4) con y′ = y − t² + 1, y(0) = 0.5, cuya solución exacta es
y = (t + 1)² − 0.5eᵗ.
