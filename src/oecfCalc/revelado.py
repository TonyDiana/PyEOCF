# -*- coding: utf-8 *-*
"""
    :Propósito: Segunda parte del análisis: el L* de la tarjeta en las
                exportaciones del revelador (TIFF), en las mismas teselas
                buenas que se eligieron en los RAW (las del análisis). El
                color de las TIFF (perfil, espacio y bits) se lee en leer
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore iinfo, imagecodecs, imread, kcom, kicc, Lightroom, lstar, oecf
# cSpell:ignore recolocadas, tifffile

__all__ = ["KRV", "MedidaTiff", "lstar_tiff", "medir_tiff"]

# --- Bibliotecas estándar Python
from pathlib import Path
from typing import NamedTuple

# --- Bibliotecas externas
import numpy as np
import tifffile

# --- Bibliotecas internas
from bib import std
from bib.oecfMediadores import KFR
from kernel import COM as KCOM
from leer import KICC, bits_tiff, espacio_tiff, lineal
from .review import Review
from .teselas import KTE


#
class KRV(std.EnumMutable):
    """ Constantes de la medida de las exportaciones del revelador. """

    # --- Holgura dentro de cada tesela, en píxeles por lado: el revelador
    #     puede corregir la distorsión del objetivo y mover algo la imagen
    HOLGURA = 4

    # --- Recorte máximo del revelador, en fracción del sensor (ancho y
    #     alto): más, y la exportación no es a tamaño completo (reducida o
    #     recortada): sus teselas caerían en otro sitio. Lightroom, en la
    #     R7, recorta un 0,3 % de ancho y un 0,4 % de alto
    RECORTE_MAX = 0.02

    # --- Por qué no se pudo medir una exportación. Compresión: una que
    #     tifffile no abre sin otra biblioteca (LZW…: imagecodecs)
    ESPACIO_DESCONOCIDO = "ESPACIO_DESCONOCIDO"
    MEDIDA_DISTINTA = "MEDIDA_DISTINTA"
    SIN_TESELAS = "SIN_TESELAS"
    COMPRIMIDA = "COMPRIMIDA"

    # --- Bits de las exportaciones definitivas (en
    #     bib/oecfMediadores/common.py: los usa también FE)
    BITS_DEFINITIVOS = KFR.BITS_DEFINITIVOS


#
# --- Lo medido en una exportación del revelador: su L* (None si no se
#     pudo medir) o por qué no (KRV; None si se midió), sus bits por
#     canal (None si no se pudo leer) y su espacio de color (una clave de
#     KICC.ESPACIOS; None si no se reconoce). Un tipo por campo: el JSON lo
#     lee un programa
class MedidaTiff(NamedTuple):
    """ Medida de una exportación del revelador: L* o motivo, bits y
    espacio. """
    lstar: float | None
    motivo: str | None
    bits: int | None
    espacio: str | None


#
def lstar_tiff(review: Review, ruta: Path) -> float | str:
    """
    L* de la tarjeta en una exportación del revelador: la mediana de las
    teselas buenas del análisis (recolocadas con el recorte del revelador,
    que se supone centrado), su color pasado a luminancia según el
    espacio de su perfil, y esta a L*. Si no se puede, por qué (KRV).
    """
    espacio = KICC.ESPACIOS.get(espacio_tiff(ruta) or "")
    if espacio is None:
        return KRV.ESPACIO_DESCONOCIDO
    try:
        imagen = tifffile.imread(ruta)
    except ValueError:
        return KRV.COMPRIMIDA
    alto, ancho = imagen.shape[:2]
    if not ((0 <= (review.alto - alto) <= (KRV.RECORTE_MAX * review.alto))
            and (0 <= (review.ancho - ancho)
            <= (KRV.RECORTE_MAX * review.ancho))):
        return KRV.MEDIDA_DISTINTA
    tope = float(np.iinfo(imagen.dtype).max)

    # --- Mediana de cada tesela buena, dentro de la imagen recortada
    lado, holgura = review.lado, KRV.HOLGURA
    dy, dx = (review.alto - alto) // 2, (review.ancho - ancho) // 2
    medianas = []
    for f, c in zip(*np.nonzero(review.motivos == KTE.BUENA)):
        y0, x0 = (f * lado) - dy + holgura, (c * lado) - dx + holgura
        y1, x1 = y0 + lado - (2 * holgura), x0 + lado - (2 * holgura)
        if (y0 >= 0) and (x0 >= 0) and (y1 <= alto) and (x1 <= ancho):
            medianas.append(np.median(
                imagen[y0:y1, x0:x1].reshape(-1, imagen.shape[2]), axis=0))
    if not medianas:
        return KRV.SIN_TESELAS
    rgb = np.median(np.array(medianas), axis=0)[:3] / tope

    # --- A luz lineal, luminancia y L*
    y = float(np.dot(espacio[1], lineal(rgb, espacio)))
    if y > KCOM.LAB_UMBRAL:
        return (KCOM.LAB_ESCALA * (y ** (1 / 3))) - KCOM.LAB_DESPLAZA
    return KCOM.LAB_PENDIENTE * y


#
def medir_tiff(review: Review, ruta: Path) -> MedidaTiff:
    """
    Todo lo que se guarda de una exportación del revelador: su L* o por
    qué no se pudo medir (ver lstar_tiff), sus bits y su espacio de color.
    """
    lstar = lstar_tiff(review, ruta)
    try:
        espacio = espacio_tiff(ruta)
    except (OSError, ValueError):
        espacio = None
    medido = isinstance(lstar, float)
    return MedidaTiff(lstar=lstar if medido else None,
                      motivo=None if medido else str(lstar),
                      bits=bits_tiff(ruta), espacio=espacio)
