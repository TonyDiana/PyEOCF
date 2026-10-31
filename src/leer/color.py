# -*- coding: utf-8 *-*
"""
    :Propósito: Color de una exportación del revelador (TIFF): su perfil
                ICC, su espacio de color y sus bits por canal. El espacio se
                reconoce por el nombre del perfil o, si tiene otro nombre
                (RawTherapee, darktable, colord…), por sus datos: colorantes
                y curva. Solo lee; medir con ello es de oecfCalc
    :Autor:     Tony Diana
    :Versión:   26.10.26
"""

# cSpell:ignore bitspersample, colord, curv, darktable, desplaz, interp
# cSpell:ignore kcom, kicc, mluc, oecf, prophoto, srgb, Therapee, tifffile

__all__ = ["KICC", "bits_tiff", "espacio_icc", "espacio_tiff", "lineal",
           "perfil_tiff"]

# --- Bibliotecas estándar Python
from functools import lru_cache
from pathlib import Path
import struct

# --- Bibliotecas externas
import numpy as np
import tifffile

# --- Bibliotecas internas
from bib import std
from kernel import COM as KCOM


#
class KICC(std.EnumMutable):
    """ Constantes de los perfiles ICC y los espacios de color. """

    # --- Espacios de color que se reconocen (por el nombre de su perfil
    #     ICC): curva que se deshace (potencia; en sRGB y ProPhoto, con su
    #     tramo lineal: umbral, pendiente, desplazamiento y escala) y
    #     coeficientes de la luminancia Y de rojo, verde y azul. La curva
    #     de sRGB es la de COM
    ADOBE = "Adobe RGB (1998)"
    SRGB = "sRGB IEC61966-2.1"
    PROPHOTO = "ProPhoto RGB"
    ESPACIOS = {
        ADOBE: ((563 / 256, None), (0.2973769, 0.6273491, 0.0752741)),
        SRGB: ((KCOM.SRGB_GAMMA,
                (KCOM.SRGB_UMBRAL_CODIFICADO, KCOM.SRGB_PENDIENTE,
                 KCOM.SRGB_DESPLAZA, KCOM.SRGB_ESCALA)),
               (0.2126390, 0.7151687, 0.0721923)),
        PROPHOTO: ((1.8, (1 / 32, 16, 0, 1)),
                   (0.2880402, 0.7118741, 0.0000857))}

    # --- Perfil ICC: inicio de su tabla de etiquetas y etiqueta y tipos de
    #     la descripción
    ICC_TABLA = 128
    ICC_ENTRADA = 12
    ICC_DESC = b"desc"
    ICC_MLUC = b"mluc"

    # --- Perfil con otro nombre (RawTherapee, darktable, colord…): se
    #     reconoce por sus datos (Tony, 2026-10-16). Colorantes rojo,
    #     verde y azul (XYZ adaptado a D50, como los guarda el ICC) de
    #     cada espacio, y lo que se pueden apartar; y la curva: la luz
    #     lineal que da en el punto medio de la escala, que debe casar
    #     con la del espacio (Rec. 709 tiene los colorantes de sRGB y
    #     otra curva). Etiquetas ICC de los colorantes y de la curva del
    #     rojo, y unidad de sus números (s15Fixed16 y u8Fixed8)
    COLORANTES = {
        SRGB: ((0.4361, 0.2225, 0.0139), (0.3851, 0.7169, 0.0971),
               (0.1431, 0.0606, 0.7141)),
        ADOBE: ((0.6097, 0.3111, 0.0195), (0.2053, 0.6257, 0.0609),
                (0.1492, 0.0632, 0.7446)),
        PROPHOTO: ((0.7977, 0.2880, 0.0000), (0.1352, 0.7119, 0.0000),
                   (0.0313, 0.0001, 0.8249))}
    TOLERANCIA_COLORANTE = 0.01
    PUNTO_MEDIO = 0.5
    TOLERANCIA_CURVA = 0.01
    ICC_COLORANTES = (b"rXYZ", b"gXYZ", b"bXYZ")
    ICC_CURVA_ROJO = b"rTRC"
    ICC_CURV = b"curv"
    ICC_PARA = b"para"

    # --- Parámetros de cada función de la curva «para» (0 a 4): g; g, a,
    #     b; g, a, b, c; g, a, b, c, d; y g, a, b, c, d, e, f
    ICC_PARAMS = (1, 3, 4, 5, 7)
    ICC_FIJO_16 = 65536
    ICC_FIJO_8 = 256


#
def perfil_tiff(ruta: Path) -> str | None:
    """ Nombre del perfil de color de una TIFF (None si no lleva). """
    icc = _icc_tiff(ruta)
    if icc is None:
        return None
    inicio = _etiquetas(icc).get(KICC.ICC_DESC)
    if inicio is not None:
        tipo = icc[inicio:inicio + 4]
        if tipo == KICC.ICC_DESC:
            largo = struct.unpack(">I", icc[inicio + 8:inicio + 12])[0]
            texto = icc[inicio + 12:inicio + 12 + largo]
            return texto.rstrip(b"\x00").decode("latin-1")
        if tipo == KICC.ICC_MLUC:
            largo, desplaz = struct.unpack(">II",
                                           icc[inicio + 20:inicio + 28])
            return icc[inicio + desplaz:inicio + desplaz
                       + largo].decode("utf-16-be")
    return None


#
def espacio_tiff(ruta: Path) -> str | None:
    """
    Espacio de color de una TIFF (una clave de KICC.ESPACIOS): por el
    nombre de su perfil y, si no se reconoce, por sus datos (ver
    espacio_icc). None si no lleva perfil o no es ninguno de los
    conocidos.
    """
    nombre = perfil_tiff(ruta)
    if nombre in KICC.ESPACIOS:
        return nombre
    icc = _icc_tiff(ruta)
    return espacio_icc(icc) if (icc is not None) else None


#
def espacio_icc(icc: bytes) -> str | None:
    """
    Espacio de color de un perfil ICC por sus datos: sus colorantes y la
    luz de su curva en el punto medio, frente a los de cada espacio
    conocido (KICC.COLORANTES). None si no casa con ninguno.
    """
    etiquetas = _etiquetas(icc)
    if not all(t in etiquetas for t in KICC.ICC_COLORANTES):
        return None
    colorantes = [struct.unpack(">3i", icc[etiquetas[t] + 8:
                                           etiquetas[t] + 20])
                  for t in KICC.ICC_COLORANTES]
    medio = _medio_curva(icc, etiquetas.get(KICC.ICC_CURVA_ROJO))
    for espacio, referencia in KICC.COLORANTES.items():
        if not all(abs((v / KICC.ICC_FIJO_16) - r)
                   <= KICC.TOLERANCIA_COLORANTE
                   for crudos, ref in zip(colorantes, referencia)
                   for v, r in zip(crudos, ref)):
            continue
        esperado = float(lineal(np.array([KICC.PUNTO_MEDIO]),
                                KICC.ESPACIOS[espacio])[0])
        if ((medio is not None)
                and (abs(medio - esperado) <= KICC.TOLERANCIA_CURVA)):
            return espacio
    return None


#
def lineal(rgb: np.ndarray, espacio: tuple) -> np.ndarray:
    """
    Luz lineal de unos valores (de 0 a 1) en un espacio de KICC.ESPACIOS:
    deshace su curva (una potencia, con o sin tramo recto).
    """
    (gamma, tramo), _ = espacio
    if tramo is None:
        return rgb ** gamma
    umbral, pendiente, desplaza, escala = tramo
    return np.where(rgb <= umbral, rgb / pendiente,
                    ((rgb + desplaza) / escala) ** gamma)


#
def bits_tiff(ruta: Path) -> int | None:
    """
    Bits por canal de una TIFF (8, 16…), o None si no se puede leer. Se
    recuerdan mientras el archivo no cambie: la ventana lo pregunta cada
    vez que rehace las incidencias.
    """
    try:
        return _bits_tiff(ruta, ruta.stat().st_mtime_ns)
    except (OSError, ValueError):
        return None


#
# --- El perfil ICC incrustado en una TIFF (None si no lleva)
def _icc_tiff(ruta: Path) -> bytes | None:
    with tifffile.TiffFile(ruta) as tif:
        etiqueta = tif.pages.first.tags.get("InterColorProfile")
        return None if (etiqueta is None) else bytes(etiqueta.value)


#
# --- Tabla de etiquetas de un perfil ICC: {firma: dónde empieza}
def _etiquetas(icc: bytes) -> dict[bytes, int]:
    n = struct.unpack(">I", icc[KICC.ICC_TABLA:KICC.ICC_TABLA + 4])[0]
    etiquetas = {}
    for i in range(n):
        desde = KICC.ICC_TABLA + 4 + (KICC.ICC_ENTRADA * i)
        firma, inicio, _ = struct.unpack(">4sII", icc[desde:desde
                                                      + KICC.ICC_ENTRADA])
        etiquetas[firma] = inicio
    return etiquetas


#
# --- Luz lineal que da una curva ICC (curv o para) en el punto medio de
#     la escala; None si no la hay o es de otro tipo
def _medio_curva(icc: bytes, inicio: int | None) -> float | None:
    if inicio is None:
        return None
    x = KICC.PUNTO_MEDIO
    tipo = icc[inicio:inicio + 4]
    if tipo == KICC.ICC_CURV:
        n = struct.unpack(">I", icc[inicio + 8:inicio + 12])[0]
        if n == 0:
            return x
        valores = struct.unpack(f">{n}H", icc[inicio + 12:inicio + 12
                                              + (2 * n)])
        if n == 1:
            return x ** (valores[0] / KICC.ICC_FIJO_8)
        return float(np.interp(x * (n - 1), range(n), valores)
                     / KCOM.MAX_16)
    if tipo == KICC.ICC_PARA:
        func = struct.unpack(">H", icc[inicio + 8:inicio + 10])[0]
        cuantos = KICC.ICC_PARAMS[func]
        crudos = struct.unpack(f">{cuantos}i",
                               icc[inicio + 12:inicio + 12 + (4 * cuantos)])
        params = [v / KICC.ICC_FIJO_16 for v in crudos]
        params += [0.0] * (max(KICC.ICC_PARAMS) - cuantos)
        g, a, b, c, d, e, f = params
        if func == 0:
            return x ** g
        if func in (1, 2):
            base = (a * x) + b
            return ((base ** g) if (base > 0) else 0.0) + (c if (func == 2)
                                                           else 0.0)
        tramo = x >= d
        if func == 3:
            return (((a * x) + b) ** g) if tramo else (c * x)
        return ((((a * x) + b) ** g) + e) if tramo else ((c * x) + f)
    return None


#
# --- Bits por canal de una TIFF, recordados por ruta y fecha de cambio
@lru_cache
def _bits_tiff(ruta: Path, _cambio: int) -> int:
    with tifffile.TiffFile(ruta) as tif:
        return int(tif.pages.first.bitspersample)
