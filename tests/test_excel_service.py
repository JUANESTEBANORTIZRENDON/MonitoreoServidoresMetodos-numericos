"""Carga del Excel real: hojas, registros, fechas, servidor y datos ausentes."""
from datetime import datetime, timedelta

import openpyxl
import pandas as pd
import pytest

from app.services.excel_service import ErrorDatosExcel, cargar_excel, verificar_consecutivas
from config import Config


def test_tres_hojas_presentes():
    libro = openpyxl.load_workbook(Config.DATA_PATH, read_only=True)
    assert libro.sheetnames == ["Resumen", "Historial", "Diccionario"]


def test_carga_resumen_y_diccionario(repo):
    assert [f["Mes"] for f in repo.resumen] == ["Agosto 2026", "Septiembre 2026", "Octubre 2026"]
    campos = [d["campo"] for d in repo.diccionario]
    assert "Temp. servidor" in campos and "Estado" in campos
    assert repo.resumen_global["Lecturas de temperatura ausentes"] == 11


def test_existen_2208_registros(repo):
    assert len(repo) == 2208


def test_fechas_consecutivas_y_servidor(repo):
    assert verificar_consecutivas(repo)
    assert repo.inicio == datetime(2026, 8, 1, 0, 0)
    assert repo.fin == datetime(2026, 10, 31, 23, 0)
    assert {l.servidor for l in repo.lecturas} == {"SRV-DC-01"}
    assert all(b.fecha_hora - a.fecha_hora == timedelta(hours=1)
               for a, b in zip(repo.lecturas, repo.lecturas[1:]))


def test_detecta_11_temperaturas_ausentes(repo):
    faltantes = repo.faltantes()
    assert len(faltantes) == 11
    assert all(l.temp_servidor is None for l in faltantes)     # nunca 0 °C
    assert all(l.estado == "Sin dato" for l in faltantes)
    assert not any(l.temp_servidor == 0 for l in repo.lecturas)


def test_archivo_inexistente_da_error_claro(tmp_path):
    with pytest.raises(ErrorDatosExcel, match="No se encontró"):
        cargar_excel(str(tmp_path / "no_existe.xlsx"))


def test_estructura_incorrecta_da_error_claro(tmp_path):
    ruta = tmp_path / "malo.xlsx"
    with pd.ExcelWriter(ruta) as w:
        pd.DataFrame({"A": [1]}).to_excel(w, sheet_name="Historial", index=False)
    with pytest.raises(ErrorDatosExcel, match="hojas requeridas"):
        cargar_excel(str(ruta))
    ruta2 = tmp_path / "malo2.xlsx"
    with pd.ExcelWriter(ruta2) as w:
        for hoja in ("Resumen", "Historial", "Diccionario"):
            pd.DataFrame({"A": [1]}).to_excel(w, sheet_name=hoja, index=False)
    with pytest.raises(ErrorDatosExcel, match="Faltan las columnas"):
        cargar_excel(str(ruta2))
