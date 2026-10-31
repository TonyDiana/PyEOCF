# -*- coding: utf-8 *-*
"""
    :Propósito: **MNS** (*Module Name Server*) del kernel: lo que no es
                interfaz ni cálculo de la app. De momento, sus constantes
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore

__all__ = ["COM", "es_mas_nueva", "K", "KA", "version_publicada"]

from .constantes import COM, K
from .update import KA, es_mas_nueva, version_publicada
