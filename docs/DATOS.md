# Datos

Archivo: `data/Historial_Monitoreo_Servidor_3_Meses.xlsx`. Es la **única fuente de datos**; la
aplicación lo lee al iniciar y nunca lo modifica.

> **Carácter sintético**: según la hoja *Diccionario*, son «Datos sintéticos para uso académico; no
> corresponden a un centro de datos real». La interfaz lo indica en el Dashboard y en el Historial.

## Hojas

| Hoja | Contenido | Uso en la app |
|------|-----------|---------------|
| **Resumen** | Indicadores mensuales (registros, CPU/RAM promedio, temperatura promedio y máxima, energía, alertas), indicadores globales y una gráfica de líneas. | Tabla de comparación en el Dashboard; prueba de carga. |
| **Historial** | 2.208 registros horarios de SRV-DC-01, 2026-08-01 00:00 → 2026-10-31 23:00. | Todos los módulos. |
| **Diccionario** | Campos, unidades, descripciones y supuestos (periodo, intervalo, umbrales, origen). | Panel «Diccionario de datos» del Historial. |

Valores globales del Resumen: 11 lecturas ausentes, temperatura máxima 88.5 °C, energía total
597.72128 kWh (suma de P·1 h), 21 horas críticas.

## Columnas de *Historial*

| Columna | Unidad / tipo | Descripción |
|---------|---------------|-------------|
| ID registro | Texto | `REG-00001` … `REG-02208` |
| Fecha y hora | Fecha y hora | Una lectura por hora, consecutivas (verificado en pruebas). |
| Servidor | Texto | Siempre `SRV-DC-01`. |
| CPU (%) | % | Uso del procesador (17.10–99.00 %). |
| RAM (%) | % | Memoria utilizada (46.82–75.99 %). |
| Potencia (W) | W | Potencia eléctrica instantánea (197.66–399.90 W). |
| Temp. entrada (°C) | °C | Aire de entrada (19.80–27.94 °C). |
| Temp. servidor (°C) | °C | Temperatura interna (45.62–88.50 °C). **11 celdas vacías intencionales.** |
| Ventilador (RPM) | RPM | Velocidad del ventilador (2115–6200 RPM). |
| Estado | Categoría | Normal, Preventivo, Crítico o Sin dato. |
| Evento | Texto | Descripción operativa. |

## Umbrales

- **Preventivo**: T ≥ 70 °C (y < 80 °C) → 101 registros.
- **Crítico**: T ≥ 80 °C → 21 registros.
- **Sin dato**: temperatura vacía → 11 registros.

Se comprobó que el `Estado` del Excel coincide exactamente con estos umbrales.

## Datos ausentes

Las 11 temperaturas vacías están en:

| Registro | Fecha y hora |
|----------|--------------|
| REG-00074 | 2026-08-04 01:00 |
| REG-00285 | 2026-08-12 20:00 |
| REG-00496 | 2026-08-21 15:00 |
| REG-00707 | 2026-08-30 10:00 |
| REG-00918 | 2026-09-08 05:00 |
| REG-01129 | 2026-09-17 00:00 |
| REG-01340 | 2026-09-25 19:00 |
| REG-01551 | 2026-10-04 14:00 |
| REG-01762 | 2026-10-13 09:00 |
| REG-01973 | 2026-10-22 04:00 |
| REG-02184 | 2026-10-30 23:00 |

Tratamiento:

- Se cargan como `None` (en vectores NumPy como `NaN`), **nunca como 0 °C**.
- Promedios y máximos del Dashboard **excluyen** esas filas.
- Las gráficas muestran un hueco en lugar de un valor.
- En el módulo de EDO, la comparación simulación–historial (`errores_serie`) solo usa las horas con
  temperatura registrada. La condición inicial es la primera lectura **válida** del periodo.

## Validaciones al cargar (`excel_service.cargar_excel`)

1. El archivo existe → si no: «No se encontró el archivo de datos en …».
2. Se abre como .xlsx.
3. Contiene las hojas *Resumen*, *Historial* y *Diccionario*.
4. *Historial* tiene las 11 columnas con sus nombres exactos.
5. «Fecha y hora» es de tipo fecha; CPU, RAM, Potencia, Temp. entrada y Ventilador son numéricas y sin
   celdas vacías; Temp. servidor es numérica (puede tener vacíos).

## Periodos usados por los módulos

- Un «día» es de 00:00 a 00:00 del día siguiente (25 lecturas, 24 subintervalos). Por eso el último
  día seleccionable en Integración y EDO (con 24 h) es 2026-10-30: el Excel termina el 31 a las 23:00.
- Ambos módulos permiten elegir la duración (1–168 h); el periodo siempre empieza a las 00:00.
- Integración usa la columna *Potencia (W)*; EDO usa *Potencia (W)* y *Temp. entrada (°C)* como entradas
  y compara con *Temp. servidor (°C)*.
