# -*- coding: utf-8 *-*
"""
    :Propósito: **MNS** (*Module Name Server*) de lo que PyOECF lee de los
                archivos de imagen: la marca y el modelo de la cámara y los
                balances de blancos propios de cada marca (cabeceras de los
                RAW), y el perfil, el espacio de color y los bits de una
                TIFF. La lectura de bajo nivel de las cabeceras TIFF
                (``leer.tiff``) es interna
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore kicc

__all__ = ["bits_tiff", "Cam", "espacio_icc", "espacio_tiff", "KC", "KICC",
           "KM", "leer_balance", "leer_cam", "leer_kelvin", "lineal",
           "perfil_tiff"]

from .cam import KC, Cam, leer_cam
from .color import (KICC, bits_tiff, espacio_icc, espacio_tiff, lineal,
                    perfil_tiff)
from .marcas import KM, leer_balance, leer_kelvin
