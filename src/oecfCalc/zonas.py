# -*- coding: utf-8 *-*
"""
    :Propósito: Posición de cada toma de la serie respecto a la Z-V
                (tercioEV: tercios de paso enteros). La zona (número y
                nombre): KP, zona_tercio y texto_zona viven en
                bib/oecfMediadores/common.py (los usa también FE)
    :Autor:     Tony Diana
    :Versión:   26.10.24
"""

# cSpell:ignore oecf

__all__ = ["calcular_tercio_exacto", "exp_relativa"]

# --- Bibliotecas estándar Python
import math

# --- Bibliotecas internas
from bib.oecfMediadores import KP


#
def exp_relativa(segundos: float, diafragma: float, iso: float) -> float:
    """Exposición relativa de una toma: t · ISO / f²."""
    return (segundos * iso) / (diafragma ** 2)


#
def calcular_tercio_exacto(exp: float, exp_ref: float) -> float:
    """Posición exacta de una toma, en tercios de paso (con decimales)
    respecto a la referencia. Positiva si tiene MÁS exposición."""
    return KP.TERCIOS * math.log2(exp / exp_ref)
