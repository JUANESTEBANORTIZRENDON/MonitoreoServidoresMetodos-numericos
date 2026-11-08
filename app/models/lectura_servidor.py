"""Modelo de una lectura horaria del servidor (una fila de la hoja Historial)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LecturaServidor:
    indice: int
    id_registro: str
    fecha_hora: datetime
    servidor: str
    cpu: float
    ram: float
    potencia: float
    temp_entrada: float
    temp_servidor: float | None   # None = dato ausente (nunca 0 °C)
    ventilador: int
    estado: str
    evento: str

    @property
    def tiene_temperatura(self) -> bool:
        return self.temp_servidor is not None and math.isfinite(self.temp_servidor)

    @property
    def temp_o_nan(self) -> float:
        return self.temp_servidor if self.tiene_temperatura else float("nan")
