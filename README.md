# Monitor Numérico de Centro de Datos

Aplicación web académica (Flask, patrón MVC) que demuestra paso a paso cómo la **integración numérica**
y las **ecuaciones diferenciales ordinarias** se aplican al monitoreo energético y térmico del servidor
**SRV-DC-01**, a partir de un historial horario de 3 meses guardado en Excel.

> Los datos del archivo `data/Historial_Monitoreo_Servidor_3_Meses.xlsx` son **sintéticos y de uso académico**.

## Módulos

| # | Módulo | Contenido |
|---|--------|-----------|
| 1 | Dashboard | Indicadores del Excel y energía total por trapecio compuesto |
| 2 | Historial del Excel | Tabla paginada en el servidor, filtros, diccionario, descarga del original |
| 3 | Integración numérica | Trapecio, Simpson 1/3, Simpson 3/8 y Romberg sobre la potencia → energía (Wh, kWh) |
| 4 | Ecuaciones diferenciales | Euler, Heun, Ralston y RK4 sobre el modelo térmico dT/dt = α(P − P_idle) − β(T − T_ent) |
| 5 | Glosario | W, Wh, kWh, potencia vs. energía, temperaturas, α, β, métodos y errores, con buscador y filtros por categoría |

Los módulos 3 y 4 están organizados para una **exposición en pareja**:

- Arriba, una **presentación por diapositivas** (10 en Integración, 11 en EDO) que se navega con
  botones, flechas ← →, puntos, gestos táctiles o un presentador (Re Pág / Av Pág). La tecla **F** o el
  botón «Pantalla completa» la amplía. El nombre del expositor se escribe en la portada y queda guardado.
  Se puede abrir una diapositiva concreta con `#diapositiva-N` en la URL.
- Abajo, los **detalles del cálculo paso a paso**: datos, fórmulas, sustituciones, tablas, gráficas e
  interpretación, como referencia para responder preguntas.

Todos los algoritmos están implementados a mano en `app/metodos_numericos/` (sin SciPy ni SymPy).
NumPy se usa solo para operaciones básicas con vectores; pandas/openpyxl solo para leer el Excel.
Las cifras de las diapositivas se calculan en el backend con los datos del Excel.

## Requisitos

- Python 3.12 o superior (verificado con Python 3.14.3 en Windows 11).
- Conexión a Internet en el navegador para cargar Bootstrap 5, Chart.js y KaTeX desde CDN.

## Instalación

```powershell
cd monitor_numerico_centro_datos
python -m venv .venv
.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate · Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```powershell
python app.py
```

Al arrancar, la consola muestra la dirección local; abra <http://127.0.0.1:5000> (glosario en <http://127.0.0.1:5000/glosario/>). Modo depuración (recarga al editar): `$env:FLASK_DEBUG = "1"; python app.py`.

Si el Excel no existe o su estructura no es la esperada, la aplicación arranca igualmente y muestra una
página de error explicando el problema. Los errores técnicos se registran en `logs/app.log`.

## Despliegue en Render

El repositorio incluye `render.yaml` (Blueprint) y `wsgi.py` (punto de entrada de producción).

1. En <https://dashboard.render.com> elija **New → Blueprint** y conecte este repositorio de GitHub.
2. Render lee `render.yaml`: instala `requirements.txt` con Python 3.12 y arranca
   `gunicorn wsgi:app --bind 0.0.0.0:$PORT`.
3. Pulse **Apply**. Al terminar, la aplicación queda en `https://monitor-numerico-centro-datos.onrender.com`
   (o el nombre que asigne Render). Cada `git push` a `main` vuelve a desplegar.

En el plan gratuito el servicio se suspende tras 15 minutos sin visitas; la primera visita siguiente tarda unos segundos.

## Pruebas

```powershell
python -m pytest -v
```

43 pruebas cubren: carga de las tres hojas, 2.208 registros, fechas consecutivas, servidor SRV-DC-01,
11 temperaturas ausentes, condiciones de Simpson 1/3 y 3/8, estructura de la tabla de Romberg,
Euler/Heun/Ralston/RK4 contra soluciones exactas (incluido su orden de convergencia), las rutas web,
las diapositivas de las presentaciones, el glosario y el punto de entrada WSGI.

## Estructura

```
monitor_numerico_centro_datos/
├── app.py                     # punto de entrada
├── config.py                  # ruta del Excel y de logs
├── data/                      # Excel original (nunca se modifica)
├── app/
│   ├── __init__.py            # fábrica Flask, carga del Excel, manejo de errores
│   ├── controllers/           # dashboard, datos, integracion, edo + comun.py (validación de formularios)
│   ├── models/                # LecturaServidor y RepositorioMonitoreo
│   ├── services/              # excel_service (lectura/validación) y monitoreo_service (datos por módulo)
│   ├── metodos_numericos/     # base, integracion, edo, interpolacion (lineal), errores (serie)
│   ├── templates/             # base, _macros, _presentacion (diapositivas) y una vista por módulo
│   └── static/                # styles.css, charts.js (Chart.js), modules.js (KaTeX, carrusel, pestañas)
├── docs/                      # ARQUITECTURA, DATOS, METODOS_NUMERICOS, GUIA_PRESENTACION
└── tests/                     # pytest
```

Más detalle en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md), [docs/DATOS.md](docs/DATOS.md),
[docs/METODOS_NUMERICOS.md](docs/METODOS_NUMERICOS.md) y [docs/GUIA_PRESENTACION.md](docs/GUIA_PRESENTACION.md).

## Decisiones relevantes

- **Día de integración**: de 00:00 a 00:00 del día siguiente (25 lecturas, 24 subintervalos). El último
  día seleccionable es 2026-10-30 porque el Excel termina el 31 a las 23:00.
- **EDO**: con α = 0.045 (valor por defecto) el modelo subestima la temperatura ≈ 19 °C; la vista calcula
  un **α calibrado** por equilibrio medio y ofrece simular con él (error promedio ≈ 3.8 °C el 1 de agosto).
- **Heun y Ralston** dan el mismo resultado en el modelo térmico porque f es lineal en T y en t dentro
  de cada hora; la interfaz lo explica y las pruebas muestran que difieren en una EDO no lineal.
