# -*- coding: utf-8 *-*
"""
    :Propósito: **MNS** (*Module Name Server*) de lo que PyOECF exporta: el
                libro Excel, el PDF, las láminas PSD y el JSON del estudio
                (que también sirve para retomar una serie). Los textos del
                libro (``exportar.excel.textos_excel``) no se exportan aquí:
                necesitan las constantes del PDF, que a su vez usa el libro,
                y exportarlos haría un círculo
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore kpdf, kpsd

__all__ = ["DatosSerie", "es_mas_nuevo", "es_preparada", "Excel",
           "grabar_json", "grabar_resultados", "grabar_revelado",
           "hay_review", "KPDF", "KPSD", "KXL", "leer_resultados",
           "leer_review", "Pdf", "Psd", "PuntoCurva", "restaurar_serie"]

from .excel import KXL, DatosSerie, Excel, PuntoCurva
from .jsonSave import (es_mas_nuevo, es_preparada, grabar_json,
                       grabar_resultados, grabar_revelado, hay_review,
                       leer_resultados, leer_review, restaurar_serie)
from .pdf import KPDF, Pdf
from .psd import KPSD, Psd
