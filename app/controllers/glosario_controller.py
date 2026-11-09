"""Módulo 5 – Glosario de términos (energía, temperatura, datos y métodos numéricos)."""
from flask import Blueprint, render_template

from app.models.glosario import CATEGORIAS, TERMINOS

bp = Blueprint("glosario", __name__, url_prefix="/glosario")


@bp.route("/")
def index():
    grupos = [(clave, nombre, icono, [t for t in TERMINOS if t["categoria"] == clave])
              for clave, nombre, icono in CATEGORIAS]
    return render_template("glosario.html", grupos=grupos, total=len(TERMINOS))
