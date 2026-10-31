# -*- coding: utf-8 *-*
"""
    :Propósito:

        **MNS** (*Module Name Server*) de las bibliotecas externas.
        Permite invocar cualquier elemento de la biblioteca con un simple:

        ``from bib import <<módulo>>``

    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore oecf

__all__ = ["oecfMediadores", "std"]

# --- OJO con el orden: oecfMediadores hace «from bib import std», así
#     que std tiene que estar ya cargado
from .std import std
from . import oecfMediadores
