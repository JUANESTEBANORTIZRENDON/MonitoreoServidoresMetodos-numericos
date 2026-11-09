"""Glosario de términos del proyecto (energía, temperatura, datos y métodos numéricos).

Cada término tiene: nombre, símbolo (LaTeX en línea o ""), unidad, definición y un ejemplo
aplicado al servidor SRV-DC-01. Las categorías se muestran en este orden en la vista.
"""
from __future__ import annotations

CATEGORIAS = [
    ("energia", "Energía y electricidad", "bi-lightning-charge"),
    ("temperatura", "Temperatura y refrigeración", "bi-thermometer-half"),
    ("datos", "Datos del monitoreo", "bi-table"),
    ("integracion", "Integración numérica", "bi-bar-chart-steps"),
    ("edo", "Ecuaciones diferenciales", "bi-graph-up-arrow"),
    ("error", "Errores y precisión", "bi-bullseye"),
]


def _t(categoria, termino, simbolo, unidad, definicion, ejemplo=""):
    return {"categoria": categoria, "termino": termino, "simbolo": simbolo, "unidad": unidad,
            "definicion": definicion, "ejemplo": ejemplo}


TERMINOS = [
    # ---------------------------------------------------------------- Energía
    _t("energia", "Potencia", r"P(t)", "W",
       "Rapidez con la que el servidor consume energía en un instante. Es lo que mide el sensor cada hora.",
       "Una lectura de 250 W significa que en ese momento el servidor consume 250 julios por segundo."),
    _t("energia", "Vatio (watt)", r"\text{W}", "W = J/s",
       "Unidad de potencia del Sistema Internacional: 1 W equivale a 1 julio de energía por segundo."),
    _t("energia", "Kilovatio", r"\text{kW}", "1 kW = 1000 W",
       "Múltiplo del vatio que se usa para cargas grandes (racks, salas completas)."),
    _t("energia", "Energía", r"E = \int P(t)\,dt", "Wh, kWh",
       "Cantidad total de trabajo eléctrico consumido durante un intervalo. Es el área bajo la curva de "
       "potencia y es lo que se factura.",
       "Si el servidor consume 250 W constantes durante 24 h, la energía es 250 × 24 = 6000 Wh."),
    _t("energia", "Vatio-hora", r"\text{Wh}", "W × h",
       "Energía que consume una carga de 1 W funcionando durante 1 hora. Es la unidad que resulta de "
       "multiplicar potencia (W) por tiempo (h) al integrar.",
       "Un trapecio de base 1 h y alturas 220 W y 240 W tiene área 1 × (220 + 240)/2 = 230 Wh."),
    _t("energia", "Kilovatio-hora", r"\text{kWh}", "1 kWh = 1000 Wh",
       "Unidad comercial de energía: la que aparece en la factura eléctrica. Se obtiene dividiendo los Wh entre 1000.",
       "6153.83 Wh ÷ 1000 = 6.15383 kWh."),
    _t("energia", "Potencia ≠ energía", "", "",
       "La potencia (W) es una tasa en un instante; la energía (Wh) es la acumulación de esa tasa en el "
       "tiempo. No se suman vatios para obtener energía: se integran.",
       "Decir «el servidor consumió 250 W en el día» es incorrecto; lo correcto es «consumió 6 kWh»."),
    _t("energia", "Potencia media", r"\bar{P} = E / \Delta t", "W",
       "Potencia constante que produciría la misma energía en el mismo tiempo.",
       "6153.83 Wh en 24 h → 6153.83 / 24 ≈ 256.4 W."),
    _t("energia", "Potencia en reposo", r"P_{idle}", "W",
       "Potencia que consume el servidor encendido pero sin carga de trabajo. En el modelo térmico, solo la "
       "potencia por encima de este valor calienta el equipo."),
    _t("energia", "Costo energético", r"C = E_{kWh} \times \text{tarifa}", "USD",
       "Valor monetario de la energía consumida. En la aplicación se usa una tarifa de referencia de 0.20 USD/kWh.",
       "6.15 kWh × 0.20 USD/kWh ≈ 1.23 USD."),
    _t("energia", "Proyección de consumo", "", "kWh",
       "Estimación de la energía en un periodo más largo a partir del consumo medido.",
       "6.15 kWh en 24 h → ≈ 184.6 kWh en 30 días."),
    _t("energia", "UPS", "", "",
       "Sistema de alimentación ininterrumpida: baterías que mantienen el servidor encendido si falla la red. "
       "Su autonomía depende de la energía (Wh) que debe suministrar."),
    _t("energia", "PUE", r"\text{PUE} = E_{total}/E_{TI}", "adimensional",
       "Power Usage Effectiveness: energía total del centro de datos dividida entre la energía de los equipos de TI. "
       "Ideal = 1.0; cuanto más alto, más energía se va en refrigeración y pérdidas."),
    _t("energia", "Huella de carbono", "", "kg CO₂",
       "Emisiones asociadas a la energía consumida: kWh × factor de emisión de la red eléctrica."),

    # ------------------------------------------------------------ Temperatura
    _t("temperatura", "Grado Celsius", r"^\circ\text{C}", "°C",
       "Unidad de temperatura usada en el Excel para el aire de entrada y para el servidor."),
    _t("temperatura", "Temperatura de entrada", r"T_{ent}(t)", "°C",
       "Temperatura del aire frío que entra al servidor. Es la referencia hacia la que el servidor tiende a enfriarse."),
    _t("temperatura", "Temperatura del servidor", r"T(t)", "°C",
       "Temperatura interna medida. Es la incógnita que se simula con la ecuación diferencial."),
    _t("temperatura", "Umbral preventivo", "", "≥ 70 °C",
       "A partir de esta temperatura la lectura se clasifica como «Preventivo»: conviene revisar refrigeración o carga."),
    _t("temperatura", "Umbral crítico", "", "≥ 80 °C",
       "A partir de esta temperatura la lectura es «Crítico»: riesgo de degradación o apagado por protección térmica."),
    _t("temperatura", "Ventilador (RPM)", "", "RPM",
       "Revoluciones por minuto del ventilador. Más RPM implica más flujo de aire y mayor enfriamiento."),
    _t("temperatura", "Coeficiente de calentamiento", r"\alpha", "°C/(h·W)",
       "Cuántos grados por hora sube la temperatura por cada vatio por encima de la potencia en reposo."),
    _t("temperatura", "Coeficiente de enfriamiento", r"\beta", "h⁻¹",
       "Rapidez con la que el servidor se acerca a la temperatura del aire de entrada (ley de enfriamiento de Newton)."),

    # ------------------------------------------------------------------ Datos
    _t("datos", "Lectura (registro)", "", "",
       "Una fila de la hoja Historial: fecha y hora, CPU, RAM, potencia, temperaturas, ventilador, estado y evento."),
    _t("datos", "Frecuencia de muestreo", "", "1 lectura/h",
       "Cada cuánto se toma una lectura. Determina el paso h de los métodos numéricos."),
    _t("datos", "Nodo", r"(t_i, P_i)", "",
       "Cada punto conocido (tiempo, valor medido). Los métodos numéricos solo usan estos puntos; no conocen la fórmula de P(t)."),
    _t("datos", "Datos tabulados", "", "",
       "Función conocida solo por una tabla de valores, no por una fórmula. Es el caso de la potencia del servidor.",
       "No sabemos P(t) = …, pero sí P(00:00) = 220 W, P(01:00) = 240 W, etc."),
    _t("datos", "Uso de CPU", "", "%",
       "Porcentaje de capacidad del procesador en uso. Suele estar relacionado con la potencia consumida."),
    _t("datos", "Uso de RAM", "", "%", "Porcentaje de memoria utilizada."),
    _t("datos", "Dato ausente", "", "",
       "Lectura sin valor (sensor sin respuesta). El Excel incluye 11 temperaturas ausentes; se informan y no se inventan."),
    _t("datos", "Estado", "", "categoría",
       "Clasificación de la lectura: Normal, Preventivo, Crítico o Sin dato, según los umbrales de temperatura."),
    _t("datos", "Datos sintéticos", "", "",
       "Datos generados para uso académico; no provienen de un centro de datos real."),

    # ------------------------------------------------------------ Integración
    _t("integracion", "Integral definida", r"\int_a^b f(t)\,dt", "",
       "Área bajo la curva de f entre a y b. Con f = potencia, la integral es la energía."),
    _t("integracion", "Integración numérica", "", "",
       "Aproximar una integral usando solo valores de la función en puntos (nodos), sin conocer su fórmula."),
    _t("integracion", "Paso", r"h", "h (horas)",
       "Distancia entre dos nodos consecutivos. Con lecturas horarias, h = 1 h.",
       "De 00:00 a 01:00 → h = 1 h."),
    _t("integracion", "Subintervalos", r"n", "",
       "Número de tramos entre la primera y la última lectura. Con n subintervalos hay n + 1 lecturas.",
       "24 h → n = 24 subintervalos y 25 lecturas."),
    _t("integracion", "Regla compuesta", "", "",
       "Aplicar una regla simple (trapecio, Simpson) en cada tramo y sumar todos los resultados."),
    _t("integracion", "Pesos", r"w_i", "",
       "Coeficiente que multiplica cada lectura en la fórmula. Indica cuántas veces «cuenta» ese punto.",
       "Trapecio: 1, 2, 2, …, 2, 1 (las lecturas interiores pertenecen a dos trapecios)."),
    _t("integracion", "Regla del trapecio compuesto", r"T = \tfrac{h}{2}\left[P_0 + 2\sum P_i + P_n\right]", "Wh",
       "Une lecturas consecutivas con rectas y suma las áreas de los trapecios. Sirve para cualquier n. Error O(h²)."),
    _t("integracion", "Simpson 1/3 compuesto", r"\tfrac{h}{3}\left[P_0 + 4\sum_{impar} + 2\sum_{par} + P_n\right]", "Wh",
       "Une cada tres lecturas con una parábola. Exige n par. Error O(h⁴)."),
    _t("integracion", "Simpson 3/8 compuesto", r"\tfrac{3h}{8}\left[P_0 + 3\sum + 2\sum_{3k} + P_n\right]", "Wh",
       "Une cada cuatro lecturas con una cúbica. Exige n múltiplo de 3. Error O(h⁴)."),
    _t("integracion", "Método de Romberg", r"R_{k,j}", "Wh",
       "Calcula trapecios con pasos cada vez más finos y los combina para cancelar el error. Exige que n permita "
       "dividir el paso a la mitad sucesivamente."),
    _t("integracion", "Extrapolación de Richardson", r"R_{k,j} = R_{k,j-1} + \tfrac{R_{k,j-1}-R_{k-1,j-1}}{4^j-1}", "",
       "Combina dos aproximaciones con pasos distintos para eliminar el término principal del error."),

    # -------------------------------------------------------------------- EDO
    _t("edo", "Ecuación diferencial ordinaria (EDO)", r"\tfrac{dT}{dt} = f(t, T)", "",
       "Ecuación que relaciona una función con su derivada. Describe cómo cambia la temperatura con el tiempo."),
    _t("edo", "Derivada (tasa de cambio)", r"\tfrac{dT}{dt}", "°C/h",
       "Cuántos grados sube (positiva) o baja (negativa) la temperatura por hora."),
    _t("edo", "Modelo térmico", r"\tfrac{dT}{dt} = \alpha(P - P_{idle}) - \beta(T - T_{ent})", "°C/h",
       "Calentamiento por la carga eléctrica menos enfriamiento por el aire de entrada."),
    _t("edo", "Condición inicial", r"T(t_0) = T_0", "°C",
       "Valor conocido al inicio de la simulación: la primera temperatura válida del Excel."),
    _t("edo", "Problema de valor inicial", "", "",
       "Una EDO más su condición inicial. Permite avanzar paso a paso desde t₀."),
    _t("edo", "Método de Euler", r"T_{k+1} = T_k + h\,f(t_k, T_k)", "",
       "Avanza con la pendiente del inicio del paso. Una evaluación de f por paso. Orden 1."),
    _t("edo", "Método de Heun", "", "",
       "Promedia la pendiente al inicio y una estimada al final del paso. Dos evaluaciones por paso. Orden 2."),
    _t("edo", "Método de Ralston", "", "",
       "Variante de orden 2 que toma la segunda pendiente a 2/3 del paso para minimizar el error."),
    _t("edo", "Runge-Kutta de orden 4 (RK4)", "", "",
       "Combina cuatro pendientes por paso (k₁ … k₄). Es el más preciso de los cuatro y se usa como referencia."),
    _t("edo", "Pendiente (k)", r"k_i", "°C/h",
       "Valor de f(t, T) evaluado en un punto del paso. Los métodos se diferencian en dónde lo evalúan y cómo lo promedian."),
    _t("edo", "Interpolación lineal", "", "",
       "Estima un valor entre dos lecturas uniéndolas con una recta. Se usa para conocer P y T_ent dentro de cada hora."),

    # ----------------------------------------------------------------- Errores
    _t("error", "Error absoluto", r"|x_{real} - x_{aprox}|", "misma unidad",
       "Diferencia entre el valor de referencia y el aproximado, sin signo."),
    _t("error", "Error de truncamiento", "", "",
       "Error que comete el método por reemplazar la curva real por rectas, parábolas o pasos finitos."),
    _t("error", "Orden del error", r"O(h^p)", "",
       "Cómo disminuye el error al reducir el paso: con O(h²), si h se divide entre 2, el error se divide aprox. entre 4."),
    _t("error", "Orden del método", r"p", "",
       "Exponente p del error global de un método de EDO: Euler 1, Heun y Ralston 2, RK4 4."),
    _t("error", "Convergencia", "", "",
       "Propiedad de que la aproximación se acerque al valor real cuando el paso h tiende a cero."),
    _t("error", "Valor de referencia", "", "",
       "Resultado más preciso disponible para comparar: Romberg en integración y RK4 en EDO."),
    _t("error", "Error promedio y máximo", "", "°C",
       "Promedio y peor caso de |T simulada − T medida| sobre todas las lecturas válidas."),
    _t("error", "Precisión de presentación", "", "5 decimales",
       "Los resultados se muestran con 5 decimales; no significa que el modelo sea exacto hasta esa cifra."),
]
