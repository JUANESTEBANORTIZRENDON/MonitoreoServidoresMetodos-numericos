# Guía de presentación (exposición en pareja)

| Expositor | Módulo | Ruta | Diapositivas |
|---|---|---|---|
| Expositor 1 | 3 · Integración numérica | <http://127.0.0.1:5000/integracion/> | 10 |
| Expositor 2 | 4 · Ecuaciones diferenciales | <http://127.0.0.1:5000/edo/> | 11 |

## Antes de empezar

1. Ejecutar `python app.py` y abrir cada módulo en una pestaña del navegador.
2. En la portada, hacer clic en «Expositor 1» / «Expositor 2» y escribir el nombre (queda guardado).
3. Pulsar **F** (o «Pantalla completa») y navegar con **← →**, Re Pág / Av Pág o un presentador.
4. Si hay que retomar, abrir `.../integracion/#diapositiva-5`.
5. Para preguntas, salir de pantalla completa (Esc) y bajar a «Detalles del cálculo paso a paso».

Los valores citados corresponden a los parámetros por defecto (1 de agosto de 2026, 24 h).

## Expositor 1 — Integración numérica (≈ 6 min)

| # | Diapositiva | Qué decir |
|---|---|---|
| 1 | Portada | Tema: cuánta energía consume un servidor; 4 métodos; resultado 6.16407 kWh. |
| 2 | El problema | El sensor mide potencia (W) cada hora; la factura y el UPS necesitan energía (kWh). E = ∫P dt. |
| 3 | Área bajo la curva | Mostrar la gráfica: 25 lecturas, la energía es el área sombreada. |
| 4 | Trapecio | Une puntos con rectas; pesos 1-2-…-2-1; 6153.83 Wh. Sirve con cualquier n. |
| 5 | Simpson 1/3 | Parábolas; requiere n par (24 cumple); 6160.23 Wh. |
| 6 | Simpson 3/8 | Cúbicas; requiere n múltiplo de 3 (24 cumple); 6158.43 Wh. |
| 7 | Romberg | Trapecios con n = 3, 6, 12, 24 y extrapolación de Richardson; 6164.07 Wh. |
| 8 | Comparación | Diferencias de pocos Wh frente a más de 6000: los métodos son consistentes. |
| 9 | Interpretación | Potencia media, costo y proyección mensual; la frecuencia de muestreo pesa más que el método. |
| 10 | ¿Qué método elegir? | El que cumpla las condiciones de los datos; trapecio como respaldo. |

**Demostración opcional**: cambiar la duración a 10 h → Simpson 3/8 no aplica; a 9 h → Simpson 1/3 y
Romberg no aplican. La plataforma lo explica en lugar de dar un resultado incorrecto.

**Transición**: «Ya sabemos cuánta energía consume el servidor; ahora mi colega mostrará qué le hace esa
energía a su temperatura».

## Expositor 2 — Ecuaciones diferenciales (≈ 7 min)

| # | Diapositiva | Qué decir |
|---|---|---|
| 1 | Portada | Gemelo digital térmico; T inicial 49.57 °C; h = 1 h, 24 pasos. |
| 2 | El problema | Predecir la temperatura para anticipar alarmas y detectar sensores defectuosos. |
| 3 | El modelo | Calor por carga α(P − P_idle) menos enfriamiento β(T − T_ent); entradas del Excel con interpolación lineal entre horas. |
| 4 | Euler | Una pendiente; primer paso k1 = −6.65060; error vs. RK4 hasta 1.63 °C. |
| 5 | Heun | Predictor–corrector, orden 2; error vs. RK4 0.22 °C. |
| 6 | Ralston | Pendiente en 3/4 del paso; coincide con Heun aquí (f lineal en T y t). |
| 7 | RK4 | Cuatro pendientes 1-2-2-1, orden 4; referencia numérica, no solución exacta. |
| 8 | Gráfica | Las cuatro curvas casi se superponen, pero quedan lejos del historial. |
| 9 | Comparación | Distinguir **error numérico** (método vs. RK4) de **error del modelo** (RK4 vs. historial ≈ 19 °C). |
| 10 | Interpretación | Pulsar «Simular con α calibrado» (≈ 0.117): el error promedio baja a ≈ 3.8 °C. |
| 11 | ¿Qué método elegir? | Precisión del método + calibración del modelo = buen gemelo digital. |

## Cierre conjunto (1 min)

«La integración nos dijo cuánta energía consume el servidor; las ecuaciones diferenciales, cómo esa
energía se convierte en temperatura. En ambos casos, elegir bien no es elegir el método más rápido, sino
el que cumple las condiciones de los datos y entrega un error controlado. Todo se calcula en Python con
el Excel real y está respaldado por 40 pruebas automáticas.»
