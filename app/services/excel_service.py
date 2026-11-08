"""Carga y validación del archivo Excel (única fuente de datos de la plataforma).

pandas y openpyxl se usan solo aquí, para leer y preparar los datos.
"""
from __future__ import annotations

import logging
import math
import os
from datetime import timedelta

import pandas as pd

from app.models.lectura_servidor import LecturaServidor
from app.models.repositorio_monitoreo import RepositorioMonitoreo

logger = logging.getLogger(__name__)

HOJAS_REQUERIDAS = ("Resumen", "Historial", "Diccionario")
COLUMNAS_HISTORIAL = (
    "ID registro", "Fecha y hora", "Servidor", "CPU (%)", "RAM (%)", "Potencia (W)",
    "Temp. entrada (°C)", "Temp. servidor (°C)", "Ventilador (RPM)", "Estado", "Evento",
)
COLUMNAS_NUMERICAS_OBLIGATORIAS = ("CPU (%)", "RAM (%)", "Potencia (W)", "Temp. entrada (°C)",
                                   "Ventilador (RPM)")


class ErrorDatosExcel(Exception):
    """El archivo no existe o su estructura no es la esperada."""


def _celdas(df: pd.DataFrame) -> list[list]:
    filas = []
    for fila in df.itertuples(index=False):
        valores = [None if (isinstance(v, float) and math.isnan(v)) else v for v in fila]
        filas.append(valores)
    return filas


def _leer_resumen(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """Extrae la tabla mensual (fila con encabezado 'Mes') y los indicadores globales."""
    filas = _celdas(df)
    mensual, global_ = [], {}
    for i, fila in enumerate(filas):
        if fila and fila[0] == "Mes":
            encabezado = [c for c in fila if c is not None]
            for f in filas[i + 1:]:
                if not f or f[0] is None:
                    break
                mensual.append(dict(zip(encabezado, f[:len(encabezado)])))
        if fila and isinstance(fila[0], str) and fila[0].startswith("Lecturas de temperatura"):
            encabezado = [c for c in fila if c is not None]
            if i + 1 < len(filas):
                global_ = dict(zip(encabezado, filas[i + 1][:len(encabezado)]))
    return mensual, global_


def _leer_diccionario(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    filas = _celdas(df)
    campos, supuestos, modo = [], [], None
    for fila in filas:
        primero = fila[0] if fila else None
        if primero == "Campo":
            modo = "campos"
            continue
        if primero == "Supuesto":
            modo = "supuestos"
            continue
        if primero is None:
            if modo == "campos":
                modo = None
            continue
        if modo == "campos" and len(fila) >= 3:
            campos.append({"campo": fila[0], "unidad": fila[1], "descripcion": fila[2]})
        elif modo == "supuestos" and len(fila) >= 2:
            supuestos.append({"supuesto": fila[0], "valor": fila[1]})
    return campos, supuestos


def validar_historial(df: pd.DataFrame) -> None:
    faltan = [c for c in COLUMNAS_HISTORIAL if c not in df.columns]
    if faltan:
        raise ErrorDatosExcel(
            "La hoja «Historial» no tiene la estructura esperada. Faltan las columnas: "
            + ", ".join(faltan))
    if df.empty:
        raise ErrorDatosExcel("La hoja «Historial» no contiene registros.")
    if not pd.api.types.is_datetime64_any_dtype(df["Fecha y hora"]):
        raise ErrorDatosExcel("La columna «Fecha y hora» debe contener fechas válidas.")
    for col in COLUMNAS_NUMERICAS_OBLIGATORIAS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ErrorDatosExcel(f"La columna «{col}» debe ser numérica.")
        if df[col].isna().any():
            raise ErrorDatosExcel(f"La columna «{col}» tiene celdas vacías inesperadas.")
    if not pd.api.types.is_numeric_dtype(df["Temp. servidor (°C)"]):
        raise ErrorDatosExcel("La columna «Temp. servidor (°C)» debe ser numérica (vacía si falta).")


def cargar_excel(ruta: str) -> RepositorioMonitoreo:
    """Lee las tres hojas, valida la estructura y construye el repositorio."""
    if not os.path.isfile(ruta):
        raise ErrorDatosExcel(
            f"No se encontró el archivo de datos en «{ruta}». Copie "
            "Historial_Monitoreo_Servidor_3_Meses.xlsx en la carpeta data/ del proyecto.")
    try:
        hojas = pd.read_excel(ruta, sheet_name=None, header=None, engine="openpyxl")
    except Exception as exc:  # archivo corrupto o no es Excel
        logger.exception("Error leyendo el Excel")
        raise ErrorDatosExcel("El archivo de datos no se pudo abrir como libro de Excel (.xlsx).") from exc

    faltan = [h for h in HOJAS_REQUERIDAS if h not in hojas]
    if faltan:
        raise ErrorDatosExcel("El Excel no contiene las hojas requeridas: " + ", ".join(faltan)
                              + f". Hojas encontradas: {', '.join(hojas)}.")

    historial = pd.read_excel(ruta, sheet_name="Historial", engine="openpyxl")
    historial.columns = [str(c).strip() for c in historial.columns]
    validar_historial(historial)
    historial = historial.sort_values("Fecha y hora").reset_index(drop=True)

    lecturas = []
    for i, fila in enumerate(historial.itertuples(index=False, name=None)):
        temp = fila[7]
        temp = None if pd.isna(temp) else float(temp)
        lecturas.append(LecturaServidor(
            indice=i, id_registro=str(fila[0]), fecha_hora=pd.Timestamp(fila[1]).to_pydatetime(),
            servidor=str(fila[2]), cpu=float(fila[3]), ram=float(fila[4]), potencia=float(fila[5]),
            temp_entrada=float(fila[6]), temp_servidor=temp, ventilador=int(fila[8]),
            estado=str(fila[9]), evento=str(fila[10]),
        ))

    resumen, resumen_global = _leer_resumen(hojas["Resumen"])
    diccionario, supuestos = _leer_diccionario(hojas["Diccionario"])
    repo = RepositorioMonitoreo(lecturas=lecturas, resumen=resumen, resumen_global=resumen_global,
                                diccionario=diccionario, supuestos=supuestos, ruta_archivo=ruta)
    logger.info("Excel cargado: %d registros, %d temperaturas ausentes", len(repo), len(repo.faltantes()))
    return repo


def verificar_consecutivas(repo: RepositorioMonitoreo, paso: timedelta = timedelta(hours=1)) -> bool:
    return all(b.fecha_hora - a.fecha_hora == paso for a, b in zip(repo.lecturas, repo.lecturas[1:]))
