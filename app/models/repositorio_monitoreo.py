"""Repositorio en memoria con las lecturas cargadas del Excel y consultas sobre ellas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import numpy as np

from .lectura_servidor import LecturaServidor

CAMPOS_ORDENABLES = {
    "id": "id_registro", "fecha": "fecha_hora", "cpu": "cpu", "ram": "ram",
    "potencia": "potencia", "temp_entrada": "temp_entrada", "temp": "temp_servidor",
    "ventilador": "ventilador", "estado": "estado", "evento": "evento",
}


@dataclass
class RepositorioMonitoreo:
    lecturas: list[LecturaServidor]
    resumen: list[dict] = field(default_factory=list)
    resumen_global: dict = field(default_factory=dict)
    diccionario: list[dict] = field(default_factory=list)
    supuestos: list[dict] = field(default_factory=list)
    ruta_archivo: str = ""

    # ------------------------------------------------------------------ básicos
    def __len__(self) -> int:
        return len(self.lecturas)

    @property
    def servidor(self) -> str:
        return self.lecturas[0].servidor if self.lecturas else ""

    @property
    def inicio(self) -> datetime:
        return self.lecturas[0].fecha_hora

    @property
    def fin(self) -> datetime:
        return self.lecturas[-1].fecha_hora

    def estados(self) -> list[str]:
        return sorted({l.estado for l in self.lecturas})

    def faltantes(self) -> list[LecturaServidor]:
        return [l for l in self.lecturas if not l.tiene_temperatura]

    # ------------------------------------------------------------------ consultas
    def filtrar(self, desde: date | None = None, hasta: date | None = None,
                estado: str | None = None, texto: str | None = None) -> list[LecturaServidor]:
        texto = (texto or "").strip().lower()
        resultado = []
        for l in self.lecturas:
            d = l.fecha_hora.date()
            if desde and d < desde:
                continue
            if hasta and d > hasta:
                continue
            if estado and l.estado != estado:
                continue
            if texto and texto not in l.evento.lower() and texto not in l.id_registro.lower() \
                    and texto not in l.fecha_hora.strftime("%Y-%m-%d %H:%M"):
                continue
            resultado.append(l)
        return resultado

    @staticmethod
    def ordenar(lecturas: list[LecturaServidor], campo: str, descendente: bool) -> list[LecturaServidor]:
        atributo = CAMPOS_ORDENABLES.get(campo, "fecha_hora")

        def clave(l: LecturaServidor):
            v = getattr(l, atributo)
            # Los datos ausentes se ubican siempre al final
            return (v is None, v if v is not None else 0)

        con = [l for l in lecturas if getattr(l, atributo) is not None]
        sin = [l for l in lecturas if getattr(l, atributo) is None]
        return sorted(con, key=clave, reverse=descendente) + sin

    def rango(self, inicio: datetime, horas: int) -> list[LecturaServidor]:
        """Lecturas desde ``inicio`` hasta ``inicio + horas`` (ambos incluidos)."""
        fin = inicio + timedelta(hours=horas)
        return [l for l in self.lecturas if inicio <= l.fecha_hora <= fin]

    # ------------------------------------------------------------------ vectores
    @staticmethod
    def vector(lecturas: list[LecturaServidor], campo: str) -> np.ndarray:
        if campo == "temp_servidor":
            return np.array([l.temp_o_nan for l in lecturas], dtype=float)
        return np.array([getattr(l, campo) for l in lecturas], dtype=float)

    @staticmethod
    def horas_relativas(lecturas: list[LecturaServidor], origen: datetime | None = None) -> list[float]:
        if not lecturas:
            return []
        origen = origen or lecturas[0].fecha_hora
        return [(l.fecha_hora - origen).total_seconds() / 3600.0 for l in lecturas]
