# -*- coding: utf-8 *-*
"""
    :Propósito: **MNS** (*Module Name Server*) del libro Excel de resultados:
                el libro y sus constantes. Los textos del libro
                (``textos_excel``) no se exportan aquí: necesitan las
                constantes del PDF, que a su vez usa este paquete,
                y exportarlos haría un círculo. Se importan aparte:
                ``from excel.textos_excel import textos_excel``
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore

__all__ = ["DatosSerie", "Excel", "KXL", "PuntoCurva"]

from .excel import KXL, DatosSerie, Excel, PuntoCurva
