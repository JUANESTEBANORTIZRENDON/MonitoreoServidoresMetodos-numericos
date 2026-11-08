"""Funcionamiento básico de las rutas de la plataforma."""
import pytest

RUTAS = ["/", "/datos/", "/integracion/", "/edo/"]


@pytest.mark.parametrize("ruta", RUTAS)
def test_rutas_principales_responden(client, ruta):
    r = client.get(ruta)
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Monitor Numérico" in html
    assert "Error interno" not in html


@pytest.mark.parametrize("ruta", ["/errores/", "/raices/", "/regresion/", "/probabilidad/", "/interpolacion/"])
def test_modulos_retirados_ya_no_existen(client, ruta):
    assert client.get(ruta).status_code == 404


def test_menu_solo_muestra_cuatro_modulos(client):
    html = client.get("/").get_data(as_text=True)
    for nombre in ("Dashboard", "Historial del Excel", "Integración numérica", "Ecuaciones diferenciales"):
        assert nombre in html
    for retirado in ("Errores numéricos", "Raíces y punto fijo", "Regresión", "Interpolación</a>"):
        assert retirado not in html


@pytest.mark.parametrize("ruta, diapositivas", [("/integracion/", 10), ("/edo/", 11)])
def test_presentaciones_tienen_diapositivas(client, ruta, diapositivas):
    html = client.get(ruta).get_data(as_text=True)
    assert html.count('class="carousel-item') == diapositivas
    assert "Detalles del cálculo paso a paso" in html


def test_historial_paginado_no_carga_todo(client):
    html = client.get("/datos/?por_pagina=25").get_data(as_text=True)
    assert html.count("<code class=\"mono\">REG-") == 25


def test_filtros_y_validacion_de_entradas(client):
    assert "Sin dato" in client.get("/datos/?estado=Sin+dato").get_data(as_text=True)
    assert "debe ser un número" in client.get("/edo/?alfa=abc").get_data(as_text=True)
    html = client.get("/integracion/?horas=10").get_data(as_text=True)
    assert "múltiplo de 3" in html


def test_descarga_excel_original(client):
    r = client.get("/datos/descargar")
    assert r.status_code == 200
    assert r.data[:2] == b"PK"
